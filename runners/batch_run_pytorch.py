#!/usr/bin/env python3
"""Batch-run apply_inputs_pytorch.py across multiple ops and inputs.csv files using venv Python.

Produces per-(csv,op) JSON under results/batch_pytorch/<csv_rel>__<op>__pytorch.json
Then produces a simple comparison report against results/batch (NumPy outputs) if present.
"""
import glob
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path('/Users/xieyushan/Documents/code')
WORKDIR = ROOT / 'Numerical_instabilities'
VENV_PY = ROOT / '.venv' / 'bin' / 'python'
HARNESS = WORKDIR / 'runners' / 'apply_inputs_pytorch.py'
OUTDIR = WORKDIR / 'results' / 'batch_pytorch'
INPUT_DIM = 16
OPS = ['div','log','exp','pow','sigmoid','softmax','sub','cossim']

os.makedirs(OUTDIR, exist_ok=True)

pattern = str(WORKDIR / '**' / 'inputs.csv')
all_csvs = [Path(p) for p in glob.glob(pattern, recursive=True)]
csvs = [p for p in all_csvs if 'results' not in p.parts and '.venv' not in p.parts]

if not csvs:
    print('No inputs.csv found under', WORKDIR)
    sys.exit(0)

summary = []
for csv in csvs:
    rel = csv.relative_to(WORKDIR)
    for op in OPS:
        safe = str(rel).replace(os.sep,'__').replace('.csv',f'__{op}__pytorch.json')
        out_path = OUTDIR / safe
        cmd = [str(VENV_PY), str(HARNESS), '--op', op, '--csv', str(csv), '--out', str(out_path)]
        print('Running:', ' '.join(cmd))
        r = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if r.returncode == 0:
            print('OK ->', out_path)
            summary.append((str(csv), op, 'ok', str(out_path)))
        else:
            print('FAIL', r.returncode)
            print('stderr:', r.stderr[:500])
            summary.append((str(csv), op, 'fail', r.stderr.strip()))

# write summary file
sum_path = OUTDIR / 'batch_pytorch_summary.json'
with open(sum_path, 'w') as f:
    json.dump({'total': len(summary), 'details': summary}, f, indent=2)
print('Wrote', sum_path)

# Now produce a simple comparison with NumPy outputs if available
numpy_dir = WORKDIR / 'results' / 'batch'
cmp_path = OUTDIR / 'comparison_summary.json'
comp = {'comparisons': []}
if numpy_dir.exists():
    # iterate over produced pytorch results and compare by filename pattern
    for csv,op,status,out in summary:
        if status!='ok':
            continue
        # build numpy counterpart path
        rel = Path(csv).relative_to(WORKDIR)
        np_file = numpy_dir / (str(rel).replace(os.sep,'__').replace('.csv','__model_numpy.json'))
        pt_file = out
        if not os.path.isfile(np_file):
            comp['comparisons'].append({'csv': csv, 'op': op, 'status': 'no_numpy'})
            continue
        try:
            with open(np_file,'r') as f:
                npd = json.load(f)
            with open(pt_file,'r') as f:
                ptd = json.load(f)
        except Exception as e:
            comp['comparisons'].append({'csv': csv, 'op': op, 'status': 'read_error', 'error': str(e)})
            continue
        # Build map testfile -> output_stats.has_nan|has_inf for quick compare
        np_map = {r['testfile']:(r.get('output') is None or r.get('output_stats',{}).get('has_nan') or r.get('output_stats',{}).get('has_inf')) for r in npd.get('results',[])}
        pt_map = {r['testfile']:(r.get('output') is None or r.get('stats',{}).get('has_nan') or r.get('stats',{}).get('has_inf')) for r in ptd.get('results',[])}
        # find mismatches where one is NaN/Inf and other is finite
        mismatches = []
        for k in set(list(np_map.keys())+list(pt_map.keys())):
            n = np_map.get(k, None)
            p = pt_map.get(k, None)
            if n is None or p is None:
                continue
            if n != p:
                mismatches.append({'testfile': k, 'numpy_bad': bool(n), 'pytorch_bad': bool(p)})
        comp['comparisons'].append({'csv': csv, 'op': op, 'mismatch_count': len(mismatches), 'examples': mismatches[:5]})
    with open(cmp_path,'w') as f:
        json.dump(comp, f, indent=2)
    print('Wrote comparison to', cmp_path)
else:
    print('NumPy batch results not found at', numpy_dir)
