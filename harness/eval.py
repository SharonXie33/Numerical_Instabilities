#!/usr/bin/env python3
"""Evaluation harness entry point.

Usage examples:
  python harness/eval.py --csv ../klee-out-1/inputs.csv --task div --out results/eval/div_report

Features:
  - run unstable vs reference implementation for an op/task
  - compute max relative error, max ULP, NaN/Inf counts, timing
  - write per-test CSV and aggregate JSON
  - optional ONNX export (for torch-backed models)
"""
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

# make project root importable when running this script directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from metrics import compute_metrics_for_pair, dtype_name


def parse_inputs(csv_path):
    """Parse an inputs.csv produced by FPGen/KLEE parser.
    Accepts rows with either: testfile, v1, v2, ...  OR v1,v2,... (no testfile).
    Returns list of (testfile, np.array(dtype=float32)).
    """
    rows = []
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for i, r in enumerate(reader):
            if not r:
                continue
            # strip whitespace
            r = [c.strip() for c in r if c.strip()!='']
            if not r:
                continue
            # If first token looks like 'test000' treat as filename
            if r[0].startswith('test') or r[0].startswith('klee') or r[0].endswith('.ktest'):
                testfile = r[0]
                tokens = r[1:]
            elif len(r) > 1 and any(t.startswith('test') for t in r):
                testfile = [t for t in r if t.startswith('test')][0]
                tokens = [t for t in r if not t.startswith('test')]
            else:
                testfile = f"row_{i:06d}"
                tokens = r
            # robust float parsing
            vals = []
            for t in tokens:
                try:
                    v = float(t)
                except Exception:
                    # handle hex or special tokens
                    try:
                        v = float(t.lower().replace('f', ''))
                    except Exception:
                        v = float('nan')
                vals.append(v)
            arr = np.array(vals, dtype=np.float32)
            rows.append((testfile, arr))
    return rows


def load_impls(task):
    # lazy import to avoid heavy deps unless needed
    if task in ('div','exp','log','pow','softmax','sigmoid','sub','cossim'):
        from models import ops_unstable, ops_ref
        return ops_unstable, ops_ref
    elif task in ('mlp', 'layernorm', 'cnn', 'attn'):
        from models import ops_unstable, ops_ref
        return ops_unstable, ops_ref
    else:
        raise ValueError(f"unknown task: {task}")


def run(csv_path, task, out_base, dtype='float32', export_onnx=False, use_torch_compile=False):
    csv_path = Path(csv_path)
    out_base = Path(out_base)
    out_base.parent.mkdir(parents=True, exist_ok=True)
    results_dir = out_base.parent / 'results' / 'eval'
    results_dir.mkdir(parents=True, exist_ok=True)

    impl_unstable, impl_ref = load_impls(task)

    inputs = parse_inputs(csv_path)
    rows_out = []
    total_start = time.perf_counter()

    for testfile, arr in inputs:
        # run unstable
        start = time.perf_counter()
        y_unstable = impl_unstable.run_task(task, arr, dtype=dtype, compile=use_torch_compile)
        t_unstable = time.perf_counter() - start

        start = time.perf_counter()
        y_ref = impl_ref.run_task(task, arr, dtype=dtype, compile=use_torch_compile)
        t_ref = time.perf_counter() - start

        # convert to numpy
        y_un = np.asarray(y_unstable, dtype=np.float64).ravel()
        y_rf = np.asarray(y_ref, dtype=np.float64).ravel()

        metrics = compute_metrics_for_pair(y_un, y_rf)
        metrics.update({
            'testfile': testfile,
            'task': task,
            'csv': str(csv_path),
            't_unstable_s': t_unstable,
            't_ref_s': t_ref,
        })
        rows_out.append(metrics)

    total_time = time.perf_counter() - total_start

    # write per-test CSV
    out_csv = results_dir / f"{csv_path.stem}__{task}__metrics.csv"
    fieldnames = ['csv','task','testfile','max_rel_error','max_ulp','nan_unstable','nan_ref','inf_unstable','inf_ref','t_unstable_s','t_ref_s']
    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows_out:
            writer.writerow({k: r.get(k,'') for k in fieldnames})

    # write summary JSON
    summary = {
        'csv': str(csv_path),
        'task': task,
        'n_tests': len(rows_out),
        'total_time_s': total_time,
        'dtype': dtype_name(dtype),
        'metrics_sample': rows_out[:5],
    }
    out_json = results_dir / f"{csv_path.stem}__{task}__summary.json"
    with open(out_json, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Wrote: {out_csv}")
    print(f"Wrote: {out_json}")
    return out_csv, out_json


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', required=True)
    p.add_argument('--task', required=True)
    p.add_argument('--out', default='results/eval')
    p.add_argument('--dtype', default='float32')
    p.add_argument('--export-onnx', action='store_true')
    p.add_argument('--torch-compile', action='store_true')
    args = p.parse_args()
    run(args.csv, args.task, args.out, dtype=args.dtype, export_onnx=args.export_onnx, use_torch_compile=args.torch_compile)


if __name__ == '__main__':
    main()
