#!/usr/bin/env python3
"""Run exported reproducers against a model (NumPy SimpleMLP or TorchScript).

Produces per-reproducer results and an aggregated JSON/CSV summary.

Usage examples:
  # Run using built-in NumPy SimpleMLP
  python tools/run_repro_on_model.py --repro results/reproducers/top20 --model numpy --out results/reproducers/top20/runs/numpy

  # Run using a TorchScript model
  python tools/run_repro_on_model.py --repro results/reproducers/top20 --model torchscript --model-path models/mymodel.pt --out results/reproducers/top20/runs/mymodel

Notes/assumptions:
- For `numpy` model we import `SimpleMLP` from `runners/test_on_model_numpy.py`.
- For `torchscript` the model must be a serialized torch.jit.ScriptModule loadable with `torch.jit.load`.
"""
import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


def load_numpy_model(input_dim: int):
    # Add project root and import the SimpleMLP class
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from runners.test_on_model_numpy import SimpleMLP
    except Exception as e:
        raise RuntimeError('failed to import SimpleMLP from runners/test_on_model_numpy.py: ' + str(e))
    return SimpleMLP(input_dim, hidden=64, out=1)


def run_numpy_model(model, arr: np.ndarray):
    # arr: 1D numpy vector; model.forward expects 2D (N,input_dim)
    X = np.array(arr, dtype=np.float32)
    if X.ndim == 1:
        X = X.reshape(1, -1)
    try:
        Y = model.forward(X)
        out = Y[0].tolist() if hasattr(Y, 'tolist') else float(Y)
        # normalize to python types
        if isinstance(out, list) and len(out) == 1:
            out = out[0]
        return {'output': out, 'error': None}
    except Exception as e:
        return {'output': None, 'error': str(e)}


def load_torchscript_model(path: str):
    try:
        import torch
    except Exception:
        raise RuntimeError('PyTorch is required for torchscript model but not available')
    try:
        m = torch.jit.load(path)
        m.eval()
        return m
    except Exception as e:
        raise RuntimeError('failed to load torchscript model: ' + str(e))


def run_torchscript_model(model, arr: np.ndarray, expected_dim: int | None = None):
    """
    Run a torchscript model with fallback shape probing.

    Tries a few candidate input shapes if the first call fails. This helps
    compatibility with models expecting (N, D), (1, D), (B, 1), etc.
    """
    import torch
    t = torch.from_numpy(np.array(arr, dtype=np.float32))

    # build candidates to try
    candidates = []
    if t.ndim == 0:
        candidates.append(t.reshape(1, 1))
    elif t.ndim == 1:
        # common shapes
        candidates.append(t.unsqueeze(0))      # (1, D)
        try:
            candidates.append(t.reshape(1, -1))
        except Exception:
            pass
        try:
            candidates.append(t.reshape(-1, 1))  # (N,1)
        except Exception:
            pass
        # if we have an expected_dim, try pad/truncate and (1, expected_dim)
        if expected_dim is not None:
            arr2 = np.zeros(expected_dim, dtype=np.float32)
            src = t.cpu().numpy().ravel()
            arr2[:min(len(src), expected_dim)] = src[:min(len(src), expected_dim)]
            candidates.append(torch.from_numpy(arr2).unsqueeze(0))
    else:
        candidates.append(t)

    last_err = None
    for cand in candidates:
        try:
            with torch.no_grad():
                out = model(cand)
            # try to convert to python numbers
            if isinstance(out, torch.Tensor):
                outv = out.cpu().numpy()
                if outv.size == 1:
                    return {'output': float(outv.reshape(-1)[0]), 'error': None}
                else:
                    return {'output': outv.tolist(), 'error': None}
            else:
                return {'output': out, 'error': None}
        except Exception as e:
            last_err = e
            # try next candidate
            continue

    # if we reach here all attempts failed
    return {'output': None, 'error': str(last_err) if last_err is not None else 'unknown error'}


def read_repro_input(path: Path):
    # prefer .npy if present, otherwise try .csv file of numeric row
    if path.suffix == '.npy':
        arr = np.load(str(path))
        return np.array(arr, dtype=np.float32)
    if path.suffix == '.csv':
        try:
            a = np.loadtxt(str(path), delimiter=',')
            if a.ndim == 0:
                a = np.array([a], dtype=np.float32)
            return np.array(a, dtype=np.float32)
        except Exception:
            # fallback: parse manually
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = [p for p in line.split(',') if p!='']
                    vals = []
                    for p in parts:
                        try:
                            vals.append(float(p))
                        except Exception:
                            # hex or nan/inf
                            lp = p.lower()
                            if lp == 'nan':
                                vals.append(float('nan'))
                            elif lp in ('inf', '+inf'):
                                vals.append(float('inf'))
                            elif lp == '-inf':
                                vals.append(float('-inf'))
                            else:
                                try:
                                    if p.startswith('0x'):
                                        vals.append(float(int(p, 16)))
                                    else:
                                        vals.append(float(p))
                                except Exception:
                                    pass
                    return np.array(vals, dtype=np.float32)
    # unknown file type: try to load as text
    with open(path, 'r') as f:
        txt = f.read().strip()
    parts = [p for p in txt.replace('\n', ',').split(',') if p!='']
    vals = []
    for p in parts:
        try:
            vals.append(float(p))
        except Exception:
            lp = p.lower()
            if lp == 'nan':
                vals.append(float('nan'))
            elif lp in ('inf', '+inf'):
                vals.append(float('inf'))
            elif lp == '-inf':
                vals.append(float('-inf'))
            else:
                try:
                    if p.startswith('0x'):
                        vals.append(float(int(p, 16)))
                except Exception:
                    pass
    return np.array(vals, dtype=np.float32)


def infer_torchscript_input_dim(model) -> int | None:
    """Try to heuristically infer a model's expected input dimension from its parameters.

    Strategy:
    - Iterate model.parameters(); for any 2D weight tensor, assume shape (out, in) and return in.
    - If not found, return None.
    """
    try:
        import torch
    except Exception:
        return None
    try:
        params = list(model.parameters())
    except Exception:
        # Some scripted modules may not expose parameters() the same way
        try:
            # try alternative attribute access
            params = []
            for name in dir(model):
                try:
                    attr = getattr(model, name)
                    if hasattr(attr, 'shape'):
                        import torch as _torch
                        if isinstance(attr, _torch.Tensor):
                            params.append(attr)
                except Exception:
                    continue
        except Exception:
            return None
    # First prefer 2D parameter shapes (e.g., Linear weight: (out, in))
    for p in params:
        try:
            s = p.shape
            if len(s) >= 2:
                # assume (out, in, ...)
                return int(s[1])
        except Exception:
            continue
    # Fall back: some modules (LayerNorm) have 1D weight/bias whose length is the
    # normalized shape (i.e., expected last-dim). Use those if present.
    for p in params:
        try:
            s = p.shape
            if len(s) == 1:
                # sanity-check size (avoid 1-element scalars)
                if int(s[0]) > 1:
                    return int(s[0])
        except Exception:
            continue
    return None


def summarize_results(rows: List[Dict[str, Any]], out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    # write JSON
    js = {'n': len(rows), 'results': rows}
    json_p = out_dir / 'summary.json'
    with open(json_p, 'w') as f:
        json.dump(js, f, indent=2)
    # write CSV
    csv_p = out_dir / 'summary.csv'
    with open(csv_p, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['repro_file', 'input_len', 'has_nan_in_input', 'has_inf_in_input', 'output', 'has_nan_in_output', 'has_inf_in_output', 'error'])
        for r in rows:
            inp = r.get('input')
            has_nan_in = bool(np.isnan(inp).any()) if inp is not None else ''
            has_inf_in = bool(np.isinf(inp).any()) if inp is not None else ''
            outv = r.get('output')
            # compute output NaN/Inf
            has_nan_out = ''
            has_inf_out = ''
            if outv is not None:
                try:
                    arr = np.array(outv, dtype=np.float64)
                    has_nan_out = bool(np.isnan(arr).any())
                    has_inf_out = bool(np.isinf(arr).any())
                except Exception:
                    has_nan_out = ''
                    has_inf_out = ''
            w.writerow([r.get('repro_file'), len(inp) if inp is not None else 0, has_nan_in, has_inf_in, json.dumps(outv), has_nan_out, has_inf_out, r.get('error') or ''])
    return json_p, csv_p


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repro', required=True, help='Directory produced by export_reproducers (contains .npy/.csv repro inputs)')
    p.add_argument('--model', required=True, choices=['numpy', 'torchscript'], help='Model type to run against')
    p.add_argument('--model-path', help='Path to model file (required for torchscript)')
    p.add_argument('--out', required=True, help='Output directory to place run summaries')
    args = p.parse_args()

    repro_dir = Path(args.repro)
    if not repro_dir.exists():
        print('repro directory not found:', repro_dir)
        raise SystemExit(2)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    model_obj = None
    if args.model == 'numpy':
        # lazy: we will infer input_dim per repro based on vector length
        model_type = 'numpy'
    else:
        if not args.model_path:
            print('--model-path is required for torchscript models')
            raise SystemExit(2)
        model_obj = load_torchscript_model(args.model_path)
        model_type = 'torchscript'
        # try to infer expected input dim for the torchscript model
        try:
            expected_dim = infer_torchscript_input_dim(model_obj)
            print('inferred torchscript input dim:', expected_dim)
        except Exception:
            expected_dim = None

    rows = []
    # discover repro files (prefer .npy/.csv)
    repro_files = sorted([p for p in repro_dir.iterdir() if p.suffix in ('.npy', '.csv')])
    if not repro_files:
        print('no repro files found in', repro_dir)
        raise SystemExit(2)

    for rp in repro_files:
        try:
            arr = read_repro_input(rp)
        except Exception as e:
            rows.append({'repro_file': str(rp), 'input': None, 'output': None, 'error': 'failed to read repro input: ' + str(e)})
            continue

        # choose model instance if numpy: create per-input-dim model
        if model_type == 'numpy':
            try:
                m = load_numpy_model(arr.shape[0])
            except Exception as e:
                rows.append({'repro_file': str(rp), 'input': arr.tolist(), 'output': None, 'error': 'failed to instantiate numpy model: ' + str(e)})
                continue
            res = run_numpy_model(m, arr)
        else:
            # if we inferred an expected dim, pad/truncate the array to that length
            if expected_dim is not None:
                if arr.ndim == 0:
                    arr = np.array([arr], dtype=np.float32)
                if arr.size < expected_dim:
                    # pad with zeros
                    na = np.zeros(expected_dim, dtype=np.float32)
                    na[:arr.size] = arr.ravel()
                    arr = na
                elif arr.size > expected_dim:
                    arr = arr.ravel()[:expected_dim]
            res = run_torchscript_model(model_obj, arr, expected_dim)

        # record
        out = res.get('output')
        err = res.get('error')
        rows.append({'repro_file': str(rp), 'input': arr.tolist(), 'output': out, 'error': err})

    js_p, csv_p = summarize_results(rows, out_dir)
    print('Wrote', js_p, csv_p)


if __name__ == '__main__':
    main()
