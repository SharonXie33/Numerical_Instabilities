#!/usr/bin/env python3
"""Export reproducer inputs for top mismatches from comparison_summary.json.

Generates per-example CSV/.npy files and a summary CSV for easy triage.
"""
import argparse
import csv
import json
import os
from pathlib import Path

import numpy as np


def find_row_for_testfile(csv_path, testfile):
    # Open CSV and look for row containing the testfile token (exact match or substring)
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for r in reader:
            if not r:
                continue
            tokens = [c.strip() for c in r if c.strip()!='']
            if not tokens:
                continue
            # testfile may be first token or anywhere
            for t in tokens:
                if t == testfile or testfile in t:
                    # return token list excluding testfile if present as first
                    # if testfile is part of tokens, remove it
                    vals = [tok for tok in tokens if tok != t and not tok.endswith('.ktest')]
                    # try to convert tokens to floats
                    out = []
                    for tok in vals:
                        try:
                            out.append(float(tok))
                        except Exception:
                            # skip non-numeric
                            pass
                    return np.array(out, dtype=np.float32), tokens
    return None, None


def export_top(input_json, top=20, examples_per=3, out_dir='results/reproducers/top20'):
    p = Path(input_json)
    root = Path.cwd()
    data = json.load(open(p, 'r'))
    comps = data.get('comparisons', [])
    comps_sorted = sorted(comps, key=lambda x: -x.get('mismatch_count',0))

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = out_dir / 'top{}_summary.csv'.format(top)
    with open(summary_path, 'w', newline='') as sf:
        writer = csv.writer(sf)
        writer.writerow(['rank','csv','op','mismatch_count','example_idx','testfile','numpy_bad','pytorch_bad','repro_csv','repro_npy'])

        rank = 0
        for comp in comps_sorted[:top]:
            rank += 1
            csv_path = comp.get('csv')
            op = comp.get('op')
            mc = comp.get('mismatch_count', 0)
            examples = comp.get('examples', [])[:examples_per]
            for ei, ex in enumerate(examples):
                testfile = ex.get('testfile')
                numpy_bad = ex.get('numpy_bad')
                pytorch_bad = ex.get('pytorch_bad')

                # resolve csv_path
                csvp = Path(csv_path)
                if not csvp.exists():
                    # try relative to repo
                    csvp = root / csv_path.lstrip('/')
                if not csvp.exists():
                    # try basename search
                    candidates = list(root.rglob(Path(csv_path).name))
                    csvp = candidates[0] if candidates else None

                repro_csv = ''
                repro_npy = ''
                if csvp and csvp.exists():
                    arr, raw_tokens = find_row_for_testfile(csvp, testfile)
                    if arr is None:
                        # try matching by testfile substring
                        arr, raw_tokens = None, None
                        with open(csvp, 'r') as f:
                            for r in csv.reader(f):
                                if any(testfile in (c or '') for c in r):
                                    vals = []
                                    for t in r:
                                        try:
                                            vals.append(float(t))
                                        except Exception:
                                            pass
                                    arr = np.array(vals, dtype=np.float32)
                                    raw_tokens = r
                                    break

                    if arr is not None:
                        name_safe = '{}__{}__{}'.format(Path(csvp).stem, op, testfile.replace('.','_'))
                        repro_csv_p = out_dir / (name_safe + '.csv')
                        repro_npy_p = out_dir / (name_safe + '.npy')
                        # write csv of numeric tokens
                        np.savetxt(repro_csv_p, arr[None,:], delimiter=',', fmt='%0.18g')
                        np.save(repro_npy_p, arr)
                        repro_csv = str(repro_csv_p)
                        repro_npy = str(repro_npy_p)
                writer.writerow([rank, csv_path, op, mc, ei, testfile, numpy_bad, pytorch_bad, repro_csv, repro_npy])

    return summary_path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default='results/batch_pytorch/comparison_summary.json')
    p.add_argument('--top', type=int, default=20)
    p.add_argument('--examples', type=int, default=3)
    p.add_argument('--out', default='results/reproducers/top20')
    args = p.parse_args()

    summary = export_top(args.input, top=args.top, examples_per=args.examples, out_dir=args.out)
    print('Wrote summary:', summary)


if __name__ == '__main__':
    main()
