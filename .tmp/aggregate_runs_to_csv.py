#!/usr/bin/env python3
"""Aggregate discovered run summary.json files into a single CSV for quick inspection.

Writes .tmp/aggregated_runs.csv in the workspace root and prints its path.
"""
import csv
import json
from pathlib import Path
import numpy as np

BASE = Path('/Users/xieyushan/Documents/code/Numerical_instabilities')
repro_base = BASE / 'results' / 'reproducers'
files = sorted(repro_base.glob('**/runs/*/summary.json'))

out_csv = BASE / '.tmp' / 'aggregated_runs.csv'
out_csv.parent.mkdir(parents=True, exist_ok=True)

with open(out_csv, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['summary_json', 'n', 'errors', 'empty_input', 'output_null', 'nan_out', 'inf_out', 'finite_out'])
    for p in files:
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        res = data.get('results', [])
        stats = {
            'n': len(res),
            'errors': 0,
            'empty_input': 0,
            'output_null': 0,
            'nan_out': 0,
            'inf_out': 0,
            'finite_out': 0,
        }
        for entry in res:
            inp = entry.get('input')
            outv = entry.get('output')
            err = entry.get('error')
            if err is not None:
                stats['errors'] += 1
            if not inp:
                stats['empty_input'] += 1
            if outv is None:
                stats['output_null'] += 1
                continue
            try:
                arr = np.array(outv, dtype=float)
            except Exception:
                try:
                    arr = np.array([float(outv)])
                except Exception:
                    arr = np.array([np.nan])
            if np.isnan(arr).any():
                stats['nan_out'] += 1
            elif np.isinf(arr).any():
                stats['inf_out'] += 1
            elif np.isfinite(arr).all():
                stats['finite_out'] += 1
        w.writerow([str(p), stats['n'], stats['errors'], stats['empty_input'], stats['output_null'], stats['nan_out'], stats['inf_out'], stats['finite_out']])

print('Wrote', out_csv)
