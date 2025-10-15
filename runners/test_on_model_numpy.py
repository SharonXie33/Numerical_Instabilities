#!/usr/bin/env python3
"""Simple NumPy-based harness to test FPGen inputs on a tiny MLP.

- Reads inputs CSV with headers: testfile,values
- Parses values into float arrays (values separated by commas)
- Pads/truncates each input to a fixed length (configurable)
- Runs a small MLP (1 hidden layer) implemented in NumPy
- Records outputs and whether outputs contain NaN/Inf
- Writes JSON results to specified output file
"""
import argparse
import csv
import json
import math
import os
from typing import List

import numpy as np


def to_number(s):
    s = s.strip()
    if s.lower() == 'nan':
        return float('nan')
    if s.lower() == 'inf' or s.lower() == '+inf':
        return float('inf')
    if s.lower() == '-inf':
        return float('-inf')
    try:
        return float(s)
    except Exception:
        if s.startswith('0x'):
            try:
                return float(int(s, 16))
            except Exception:
                return float('nan')
        return float('nan')


class SimpleMLP:
    def __init__(self, input_dim, hidden=32, out=1, seed=123):
        rng = np.random.RandomState(seed)
        self.W1 = rng.normal(scale=0.1, size=(input_dim, hidden)).astype(np.float32)
        self.b1 = np.zeros(hidden, dtype=np.float32)
        self.W2 = rng.normal(scale=0.1, size=(hidden, out)).astype(np.float32)
        self.b2 = np.zeros(out, dtype=np.float32)

    def forward(self, x: np.ndarray) -> np.ndarray:
        # x: (N, input_dim)
        h = x.dot(self.W1) + self.b1
        # ReLU
        h = np.maximum(h, 0)
        y = h.dot(self.W2) + self.b2
        return y


def read_csv_inputs(path: str) -> List[dict]:
    rows = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def prepare_array(vals_list, target_len):
    arr = np.zeros((len(vals_list), target_len), dtype=np.float32)
    for i, vals in enumerate(vals_list):
        n = min(len(vals), target_len)
        if n>0:
            arr[i, :n] = vals[:n]
    return arr


def check_stats(arr: np.ndarray):
    flat = arr.flatten()
    has_nan = np.isnan(flat).any()
    has_inf = np.isinf(flat).any()
    finite = flat[np.isfinite(flat)]
    minv = float(np.min(finite)) if finite.size>0 else None
    maxv = float(np.max(finite)) if finite.size>0 else None
    meanv = float(np.mean(finite)) if finite.size>0 else None
    return {'has_nan': bool(has_nan), 'has_inf': bool(has_inf), 'min': minv, 'max': maxv, 'mean': meanv}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', required=True, help='inputs CSV file (testfile,values)')
    p.add_argument('--out', required=True, help='output JSON file')
    p.add_argument('--input-dim', type=int, default=64, help='fixed input vector length to pad/truncate to')
    args = p.parse_args()

    if not os.path.isfile(args.csv):
        print('csv not found:', args.csv)
        raise SystemExit(2)

    rows = read_csv_inputs(args.csv)
    parsed = []
    vals_list = []
    for r in rows:
        fname = r.get('testfile') or r.get('test') or 'unknown'
        vals_field = r.get('values') or ''
        parts = [s for s in vals_field.split(',') if s!='']
        vals = [to_number(s) for s in parts]
        parsed.append({'testfile': fname, 'values': vals})
        vals_list.append(vals)

    X = prepare_array(vals_list, args.input_dim)
    model = SimpleMLP(args.input_dim, hidden=64, out=1)
    Y = model.forward(X)

    results = []
    for i, rec in enumerate(parsed):
        input_stats = check_stats(np.array(rec['values'], dtype=np.float32))
        output_stats = check_stats(Y[i:i+1])
        results.append({'testfile': rec['testfile'], 'input_len': len(rec['values']), 'input_stats': input_stats, 'output': float(Y[i,0]) if np.isfinite(Y[i,0]) else None, 'output_stats': output_stats})

    out_payload = {'model': 'SimpleNumPyMLP', 'input_dim': args.input_dim, 'n_tests': len(results), 'results': results}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w') as f:
        json.dump(out_payload, f, indent=2)
    print('wrote', args.out, 'tests:', len(results))


if __name__ == '__main__':
    main()
