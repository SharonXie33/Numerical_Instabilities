#!/usr/bin/env python3
"""Apply FPGen/KLEE-generated inputs to simple operator implementations.

This script prefers PyTorch if installed; otherwise falls back to NumPy.

Usage:
  python runners/apply_inputs_pytorch.py --op div --csv path/to/inputs.csv --out results/div.json
"""
import argparse
import csv
import json
import math
import os
import sys

try:
    import torch
    has_torch = True
except Exception:
    has_torch = False
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
        # hex fallback
        if s.startswith('0x'):
            try:
                return float(int(s, 16))
            except Exception:
                return s
        return s


def check_stats(vals):
    # vals: iterable of numbers (float or numpy/torch)
    nan = any(math.isnan(float(x)) for x in vals)
    inf = any(math.isinf(float(x)) for x in vals)
    return {'has_nan': nan, 'has_inf': inf}


def run_op(op, values):
    # values: list of floats
    if has_torch:
        t = torch.tensor(values, dtype=torch.float32)
        if op == 'div':
            a = t[0]
            b = t[1]
            out = a / b
            outv = out.item()
        elif op == 'sub':
            out = t[0] - t[1]
            outv = out.item()
        elif op == 'pow':
            out = torch.pow(t[0], t[1]) if t.numel()>=2 else torch.pow(t[0], t[0])
            outv = out.item()
        elif op == 'log':
            out = torch.log(t[0])
            outv = out.item()
        elif op == 'exp':
            out = torch.exp(t[0])
            outv = out.item()
        elif op == 'sigmoid':
            out = torch.sigmoid(t[0])
            outv = out.item()
        elif op == 'softmax':
            out = torch.nn.functional.softmax(t, dim=0)
            outv = [float(x.item()) for x in out]
        elif op == 'cossim':
            # expect values representing two equal-length vectors; split in half
            n = len(values)
            half = n // 2
            a = t[:half]
            b = t[half:half*2]
            denom = torch.norm(a) * torch.norm(b)
            if denom == 0:
                outv = float('nan')
            else:
                outv = float(torch.dot(a, b) / denom)
        else:
            raise ValueError('unsupported op ' + op)
        # stats
        if isinstance(outv, list):
            stats = check_stats(outv)
        else:
            stats = check_stats([outv])
        return outv, stats
    else:
        # numpy fallback
        arr = np.array(values, dtype=np.float32)
        if op == 'div':
            a = arr[0]; b = arr[1]
            try:
                out = a / b
            except Exception:
                out = float('nan')
            outv = float(out)
        elif op == 'sub':
            outv = float(arr[0] - arr[1])
        elif op == 'pow':
            outv = float(np.power(arr[0], arr[1]) if arr.size>=2 else np.power(arr[0], arr[0]))
        elif op == 'log':
            try:
                outv = float(np.log(arr[0]))
            except Exception:
                outv = float('nan')
        elif op == 'exp':
            try:
                outv = float(np.exp(arr[0]))
            except Exception:
                outv = float('nan')
        elif op == 'sigmoid':
            outv = float(1.0 / (1.0 + np.exp(-arr[0])))
        elif op == 'softmax':
            e = np.exp(arr - np.max(arr))
            s = e / (np.sum(e) if np.sum(e)!=0 else 1.0)
            outv = [float(x) for x in s]
        elif op == 'cossim':
            n = len(values)
            half = n // 2
            a = arr[:half]
            b = arr[half:half*2]
            denom = np.linalg.norm(a) * np.linalg.norm(b)
            outv = float(np.dot(a,b)/denom) if denom!=0 else float('nan')
        else:
            raise ValueError('unsupported op ' + op)
        stats = check_stats([outv] if not isinstance(outv, list) else outv)
        return outv, stats


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--op', required=True, help='Operator to test (div, log, exp, softmax, pow, sigmoid, sub, cossim)')
    p.add_argument('--csv', required=True, help='Path to inputs.csv produced by ktest_to_inputs.py')
    p.add_argument('--out', required=True, help='Output JSON file for results')
    args = p.parse_args()

    if not os.path.isfile(args.csv):
        print('csv not found:', args.csv, file=sys.stderr)
        sys.exit(2)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    results = []
    with open(args.csv, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = row['testfile']
            vals_field = row['values']
            # split by comma, but values may already be a single value
            parts = [s for s in vals_field.split(',') if s!='']
            vals = [to_number(s) for s in parts]
            try:
                outv, stats = run_op(args.op, vals)
            except Exception as e:
                outv = None
                stats = {'error': str(e)}
            results.append({'testfile': fname, 'input': vals, 'output': outv, 'stats': stats})

    with open(args.out, 'w') as f:
        json.dump({'op': args.op, 'has_torch': has_torch, 'results': results}, f, indent=2)
    print('wrote', args.out, 'tests:', len(results))


if __name__ == '__main__':
    main()
