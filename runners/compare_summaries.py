#!/usr/bin/env python3
"""Aggregate run summaries under results/runs/** and produce reports.

Produces:
  - report/aggregated_runs.csv  (one row per model/framework/dataset/run)
  - report/framework_diff.csv   (per run+model+dataset summary across frameworks)
  - report/summary.md          (human-readable summary)

Usage: python runners/compare_summaries.py --root results/runs --out report
"""
import argparse
import glob
import json
import os
import csv
from collections import defaultdict, Counter


def find_summary_files(root):
    pattern = os.path.join(root, '**', 'summary.json')
    return glob.glob(pattern, recursive=True)


def load_summary(path):
    try:
        with open(path) as f:
            data = json.load(f)
        # Expect data to be a list of entries
        if isinstance(data, dict) and 'summary' in data:
            data = data['summary']
        if not isinstance(data, list):
            return []
        return data
    except Exception as e:
        print('failed to load', path, e)
        return []


def ensure_dir(d):
    os.makedirs(d, exist_ok=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='results/runs', help='root directory containing run folders')
    p.add_argument('--out', default='report', help='output folder for aggregated reports')
    args = p.parse_args()

    summary_files = find_summary_files(args.root)
    if not summary_files:
        print('no summary.json files found under', args.root)
        return 1

    ensure_dir(args.out)

    agg_csv = os.path.join(args.out, 'aggregated_runs.csv')
    diff_csv = os.path.join(args.out, 'framework_diff.csv')
    md_path = os.path.join(args.out, 'summary.md')

    # aggregated rows
    agg_rows = []

    # per-run, per-model,dataset map: run -> (model,dataset) -> framework -> stats
    per_run = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    # global counters
    fw_counter = Counter()
    model_nan_counter = Counter()

    for sf in summary_files:
        run_dir = os.path.dirname(sf)
        run_name = os.path.relpath(run_dir, args.root)
        entries = load_summary(sf)
        for e in entries:
            model = e.get('model') or e.get('model_name') or 'UNKNOWN'
            fw = e.get('framework') or e.get('framework_name') or 'UNKNOWN'
            ds = e.get('dataset') or e.get('dataset_name') or 'UNKNOWN'
            total = e.get('total', 0)
            num_nan = e.get('num_nan', 0)
            num_inf = e.get('num_inf', 0)
            num_error = e.get('num_error', 0)

            agg_rows.append([run_name, model, fw, ds, total, num_nan, num_inf, num_error])

            per_run[run_name][(model, ds)][fw] = {'total': total, 'num_nan': num_nan, 'num_inf': num_inf, 'num_error': num_error}

            fw_counter[fw] += 1
            model_nan_counter[model] += num_nan

    # write aggregated_runs.csv
    with open(agg_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['run', 'model', 'framework', 'dataset', 'total', 'num_nan', 'num_inf', 'num_error'])
        for r in agg_rows:
            w.writerow(r)

    # write framework_diff.csv: per run, per model/dataset list frameworks and stats
    with open(diff_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['run', 'model', 'dataset', 'frameworks', 'stats_json', 'max_nan', 'max_inf', 'max_error'])
        for run, md_map in per_run.items():
            for (model, ds), fw_map in md_map.items():
                fw_list = sorted(fw_map.keys())
                stats_json = json.dumps(fw_map, ensure_ascii=False)
                max_nan = max((v.get('num_nan', 0) for v in fw_map.values()), default=0)
                max_inf = max((v.get('num_inf', 0) for v in fw_map.values()), default=0)
                max_err = max((v.get('num_error', 0) for v in fw_map.values()), default=0)
                w.writerow([run, model, ds, '|'.join(fw_list), stats_json, max_nan, max_inf, max_err])

    # write summary.md
    top_models = model_nan_counter.most_common(10)
    with open(md_path, 'w') as f:
        f.write('# Aggregated runs summary\n\n')
        f.write(f'- total runs: {len(per_run)}\n')
        f.write(f'- total summary files: {len(summary_files)}\n')
        f.write(f'- frameworks seen: {', '.join(sorted(fw_counter.keys()))}\n')
        f.write('\n')
        f.write('## Top models by total NaN count (across all runs & frameworks)\n')
        if top_models:
            f.write('\n')
            for m, c in top_models:
                f.write(f'- {m}: {c} NaNs\n')
        else:
            f.write('\nNo NaN records found.\n')

        f.write('\n## Quick stats\n')
        total_rows = len(agg_rows)
        total_nan = sum(int(r[5]) for r in agg_rows)
        total_inf = sum(int(r[6]) for r in agg_rows)
        total_err = sum(int(r[7]) for r in agg_rows)
        f.write(f'- total model-framework-dataset entries: {total_rows}\n')
        f.write(f'- total NaNs observed: {total_nan}\n')
        f.write(f'- total Infs observed: {total_inf}\n')
        f.write(f'- total Errors observed: {total_err}\n')

    print('wrote', agg_csv, diff_csv, md_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
