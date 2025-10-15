#!/usr/bin/env python3
"""Run ONNX models on repro inputs and produce summary.json / summary.csv like the torch runner.
"""
import argparse
from pathlib import Path
import onnxruntime as ort
import numpy as np
import json
import csv


def read_repro_input(path: Path):
    if path.suffix == '.npy':
        return np.load(str(path)).astype(np.float32)
    if path.suffix == '.csv':
        try:
            a = np.loadtxt(str(path), delimiter=',')
            if a.ndim == 0:
                a = np.array([a], dtype=np.float32)
            return a.astype(np.float32)
        except Exception:
            txt = path.read_text().strip()
            parts = [p for p in txt.replace('\n', ',').split(',') if p!='']
            vals = []
            for p in parts:
                try:
                    vals.append(float(p))
                except Exception:
                    lp = p.lower()
                    if lp == 'nan':
                        vals.append(np.nan)
                    elif lp in ('inf','+inf'):
                        vals.append(np.inf)
                    elif lp == '-inf':
                        vals.append(-np.inf)
            return np.array(vals, dtype=np.float32)
    txt = path.read_text().strip()
    parts = [p for p in txt.replace('\n', ',').split(',') if p!='']
    vals = []
    for p in parts:
        try:
            vals.append(float(p))
        except Exception:
            lp = p.lower()
            if lp == 'nan':
                vals.append(np.nan)
            elif lp in ('inf','+inf'):
                vals.append(np.inf)
            elif lp == '-inf':
                vals.append(-np.inf)
    return np.array(vals, dtype=np.float32)


def run_session(sess, arr: np.ndarray):
    # find input name
    input_name = sess.get_inputs()[0].name
    # prepare input
    x = arr
    if x.ndim == 1:
        x = x.reshape(1, -1)
    try:
        res = sess.run(None, {input_name: x.astype(np.float32)})
        out = res[0]
        if isinstance(out, np.ndarray) and out.size == 1:
            return float(out.reshape(-1)[0]), None
        return out.tolist(), None
    except Exception as e:
        return None, str(e)


def summarize(rows, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    js = {'n': len(rows), 'results': rows}
    with open(outdir / 'summary.json', 'w') as f:
        json.dump(js, f, indent=2)
    with open(outdir / 'summary.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['repro_file','input_len','has_nan_in','has_inf_in','output','has_nan_out','has_inf_out','error'])
        for r in rows:
            inp = r.get('input')
            has_nan_in = bool(np.isnan(inp).any()) if inp is not None else ''
            has_inf_in = bool(np.isinf(inp).any()) if inp is not None else ''
            outv = r.get('output')
            has_nan_out = ''
            has_inf_out = ''
            if outv is not None:
                try:
                    arr = np.array(outv, dtype=float)
                    has_nan_out = bool(np.isnan(arr).any())
                    has_inf_out = bool(np.isinf(arr).any())
                except Exception:
                    pass
            w.writerow([r.get('repro_file'), len(inp) if inp is not None else 0, has_nan_in, has_inf_in, json.dumps(outv), has_nan_out, has_inf_out, r.get('error') or ''])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--onnx', required=True)
    p.add_argument('--repro', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()

    onnx_p = Path(args.onnx)
    repro = Path(args.repro)
    outdir = Path(args.out)

    sess = ort.InferenceSession(str(onnx_p))
    repro_files = sorted([q for q in repro.iterdir() if q.suffix in ('.npy', '.csv')])
    rows = []
    for rp in repro_files:
        try:
            arr = read_repro_input(rp)
        except Exception as e:
            rows.append({'repro_file': str(rp), 'input': None, 'output': None, 'error': 'read error: '+str(e)})
            continue
        out, err = run_session(sess, arr)
        rows.append({'repro_file': str(rp), 'input': arr.tolist() if arr is not None else None, 'output': out, 'error': err})

    summarize(rows, outdir)
    print('Wrote', outdir / 'summary.json')


if __name__ == '__main__':
    main()
