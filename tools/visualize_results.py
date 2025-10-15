#!/usr/bin/env python3
"""Generate visualizations from report CSVs.

Creates multiple charts in the report directory:
  - instability_by_op_bar.png  (stacked bar: NaN / Inf / Errors per model)
  - framework_diff_heatmap.png (heatmap: NaN count per model vs framework)
  - framework_counts_bar.png   (counts of entries per framework)
  - model_nan_percent.png      (percent of NaN per model)

Usage:
  python tools/visualize_results.py --report-dir report --out-dir report
"""
import argparse
import csv
import os
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt


def read_aggregated(path):
    rows = []
    with open(path) as f:
        r = csv.DictReader(f)
        for row in r:
            for k in ('total', 'num_nan', 'num_inf', 'num_error'):
                if row.get(k) is None or row[k] == '':
                    row[k] = 0
                else:
                    try:
                        row[k] = int(row[k])
                    except Exception:
                        row[k] = 0
            rows.append(row)
    return rows


def make_instability_bar(rows, out_path):
    agg = defaultdict(lambda: {'nan': 0, 'inf': 0, 'err': 0})
    for r in rows:
        model = r.get('model', 'UNKNOWN')
        agg[model]['nan'] += int(r.get('num_nan', 0))
        agg[model]['inf'] += int(r.get('num_inf', 0))
        agg[model]['err'] += int(r.get('num_error', 0))

    models = sorted(agg.keys())
    nan_vals = [agg[m]['nan'] for m in models]
    inf_vals = [agg[m]['inf'] for m in models]
    err_vals = [agg[m]['err'] for m in models]

    x = np.arange(len(models))
    width = 0.6

    plt.figure(figsize=(max(8, len(models)*0.5), 6))
    plt.bar(x, nan_vals, width, label='NaN', color='#d62728')
    plt.bar(x, inf_vals, width, bottom=nan_vals, label='Inf', color='#9467bd')
    bottom_err = [nan_vals[i] + inf_vals[i] for i in range(len(nan_vals))]
    plt.bar(x, err_vals, width, bottom=bottom_err, label='Errors', color='#7f7f7f')

    plt.ylabel('Count')
    plt.title('Instability counts by model (NaN / Inf / Errors)')
    plt.xticks(x, models, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def make_framework_heatmap(rows, out_path):
    models = sorted({r['model'] for r in rows})
    frameworks = sorted({r['framework'] for r in rows})
    if not models or not frameworks:
        # nothing to draw
        return
    m_idx = {m:i for i,m in enumerate(models)}
    f_idx = {f:i for i,f in enumerate(frameworks)}

    mat = np.zeros((len(models), len(frameworks)), dtype=float)
    for r in rows:
        m = r['model']
        f = r['framework']
        mat[m_idx[m], f_idx[f]] += int(r.get('num_nan', 0))

    plt.figure(figsize=(max(6, len(frameworks)*1.2), max(6, len(models)*0.4)))
    im = plt.imshow(mat, aspect='auto', cmap='viridis')
    plt.colorbar(im, label='Sum num_nan')
    plt.xticks(range(len(frameworks)), frameworks, rotation=45, ha='right')
    plt.yticks(range(len(models)), models)
    plt.title('Framework vs Model: NaN counts heatmap')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def make_framework_counts_bar(rows, out_path):
    counts = defaultdict(int)
    for r in rows:
        counts[r.get('framework', 'UNKNOWN')] += 1
    frameworks = sorted(counts.keys())
    vals = [counts[f] for f in frameworks]

    x = np.arange(len(frameworks))
    plt.figure(figsize=(max(6, len(frameworks)*1.2), 4))
    plt.bar(x, vals, color='#1f77b4')
    plt.xticks(x, frameworks, rotation=45, ha='right')
    plt.ylabel('Entries')
    plt.title('Number of entries per framework')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def make_model_nan_percent(rows, out_path):
    agg = defaultdict(lambda: {'nan': 0, 'total': 0})
    for r in rows:
        model = r.get('model', 'UNKNOWN')
        agg[model]['nan'] += int(r.get('num_nan', 0))
        agg[model]['total'] += int(r.get('total', 0))

    models = sorted(agg.keys())
    perc = []
    for m in models:
        total = agg[m]['total']
        nan = agg[m]['nan']
        p = (nan / total * 100.0) if total > 0 else 0.0
        perc.append(p)

    x = np.arange(len(models))
    plt.figure(figsize=(max(8, len(models)*0.5), 5))
    plt.bar(x, perc, color='#ff7f0e')
    plt.xticks(x, models, rotation=45, ha='right')
    plt.ylabel('NaN %')
    plt.title('Percentage of NaN observations per model')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--report-dir', default='report', help='report directory containing aggregated CSVs')
    p.add_argument('--out-dir', default=None, help='output directory for images (defaults to report-dir)')
    args = p.parse_args()

    out_dir = args.out_dir or args.report_dir
    os.makedirs(out_dir, exist_ok=True)

    agg_csv = os.path.join(args.report_dir, 'aggregated_runs.csv')
    if not os.path.exists(agg_csv):
        raise SystemExit(f'aggregated CSV not found: {agg_csv}')

    rows = read_aggregated(agg_csv)

    make_instability_bar(rows, os.path.join(out_dir, 'instability_by_op_bar.png'))
    make_framework_heatmap(rows, os.path.join(out_dir, 'framework_diff_heatmap.png'))
    make_framework_counts_bar(rows, os.path.join(out_dir, 'framework_counts_bar.png'))
    make_model_nan_percent(rows, os.path.join(out_dir, 'model_nan_percent.png'))

    print('wrote images to', out_dir)


if __name__ == '__main__':
    main()
