#!/usr/bin/env python3
"""
Aggregate JSON results from different runtimes/frameworks into CSV and Markdown summary.

Usage: python3 tools/compute_summary_stats.py --dir results/models_eval --out results/models_summary
"""
import os
import glob
import json
import csv
import argparse

def summarize(json_files):
    rows = []
    for jf in json_files:
        j = json.load(open(jf))
        model = j.get('model') or os.path.basename(jf)
        total = len(j.get('results', []))
        n_nan = sum(1 for r in j.get('results',[]) if r.get('stats',{}).get('has_nan'))
        n_inf = sum(1 for r in j.get('results',[]) if r.get('stats',{}).get('has_inf'))
        rows.append((os.path.basename(jf), model, total, n_nan, n_inf))
    return rows

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dir', required=True)
    p.add_argument('--out', default='results/models_summary')
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    js = glob.glob(os.path.join(args.dir, '*.json'))
    rows = summarize(js)
    csvp = os.path.join(args.out, 'models_summary.csv')
    with open(csvp,'w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['file','model','tests','has_nan','has_inf'])
        w.writerows(rows)
    mdp = os.path.join(args.out, 'models_summary.md')
    with open(mdp,'w') as f:
        f.write('# Models summary\n\n')
        f.write('|file|model|tests|has_nan|has_inf|\n')
        f.write('|---|---|---:|---:|---:|\n')
        for r in rows:
            f.write('|%s|%s|%d|%d|%d|\n' % r)
    print('wrote', csvp, mdp)

if __name__ == '__main__':
    main()
