#!/usr/bin/env python3
"""Batch-run the NumPy harness over all inputs.csv files under Numerical_instabilities.

For each found inputs.csv, this script will:
- skip files under results/ to avoid recursive output
- produce an output JSON in Numerical_instabilities/results/batch/<relative_path>__model_numpy.json
- call the harness using the workspace venv Python (/Users/xieyushan/Documents/code/.venv/bin/python)
- collect per-file return codes and at the end print a small summary
"""
import glob
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path('/Users/xieyushan/Documents/code')
WORKDIR = ROOT / 'Numerical_instabilities'
VENV_PY = ROOT / '.venv' / 'bin' / 'python'
HARNESS = WORKDIR / 'runners' / 'test_on_model_numpy.py'
OUTDIR = WORKDIR / 'results' / 'batch'
INPUT_DIM = 16

os.makedirs(OUTDIR, exist_ok=True)

# find inputs.csv under Numerical_instabilities
pattern = str(WORKDIR / '**' / 'inputs.csv')
all_csvs = [Path(p) for p in glob.glob(pattern, recursive=True)]
# filter out results dir and any files under .venv etc
csvs = [p for p in all_csvs if 'results' not in p.parts and '.venv' not in p.parts]

if not csvs:
    print('No inputs.csv found under', WORKDIR)
    sys.exit(0)

print(f'Found {len(csvs)} inputs.csv files; running harness on each')

summary = []
for csv in csvs:
    rel = csv.relative_to(WORKDIR)
    out_name = str(rel).replace(os.sep, '__').replace('.csv', '__model_numpy.json')
    out_path = OUTDIR / out_name
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [str(VENV_PY), str(HARNESS), '--csv', str(csv), '--out', str(out_path), '--input-dim', str(INPUT_DIM)]
    print('\nRunning:', ' '.join(cmd))
    try:
        r = subprocess.run(cmd, check=False, capture_output=True, text=True)
    except Exception as e:
        print('Failed to run:', e)
        summary.append((str(csv), 'error', str(e)))
        continue

    if r.returncode == 0:
        print('OK ->', out_path)
        summary.append((str(csv), 'ok', str(out_path)))
    else:
        print('FAILED returncode=', r.returncode)
        print('stdout:', r.stdout[:1000])
        print('stderr:', r.stderr[:1000])
        summary.append((str(csv), f'failed({r.returncode})', r.stderr.strip()))

# print final summary
ok = sum(1 for s in summary if s[1] == 'ok')
fail = len(summary) - ok
print('\nBatch finished. total:', len(summary), 'ok:', ok, 'fail:', fail)
for s in summary:
    print('-', s[0], '->', s[1])

# Optionally, produce a small aggregated report across generated JSONs
import json
agg = {'total_files': len(summary), 'processed': [], 'total_tests': 0, 'nan_inf_tests': 0}
for s in summary:
    if s[1] != 'ok':
        continue
    try:
        with open(s[2], 'r') as f:
            data = json.load(f)
    except Exception:
        continue
    n_tests = data.get('n_tests', 0)
    agg['total_tests'] += n_tests
    nan_inf = 0
    examples = []
    for r in data.get('results', []):
        if r.get('output_stats', {}).get('has_nan') or r.get('output_stats', {}).get('has_inf'):
            nan_inf += 1
            if len(examples) < 3:
                examples.append({'testfile': r.get('testfile'), 'input_stats': r.get('input_stats'), 'output_stats': r.get('output_stats')})
    agg['nan_inf_tests'] += nan_inf
    agg['processed'].append({'csv': s[0], 'out': s[2], 'n_tests': n_tests, 'nan_inf': nan_inf, 'examples': examples})

agg_path = OUTDIR / 'batch_summary.json'
with open(agg_path, 'w') as f:
    json.dump(agg, f, indent=2)
print('Wrote aggregate summary to', agg_path)
