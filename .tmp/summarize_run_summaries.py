#!/usr/bin/env python3
import json
import math
from pathlib import Path

BASE = Path('/Users/xieyushan/Documents/code/Numerical_instabilities')
files = [
    BASE / 'results/reproducers/top20/runs/small_classifier/summary.json',
    BASE / 'results/reproducers/top20/runs/small_layernorm/summary.json',
    BASE / 'results/reproducers/top20/runs/tiny_attention/summary.json',
]
out = {}
for p in files:
    if not p.exists():
        out[str(p)] = {'error': 'missing'}
        continue
    j = json.loads(p.read_text())
    n = j.get('n', None)
    results = j.get('results', [])
    cnt_error = 0
    cnt_empty_input = 0
    cnt_nan_out = 0
    cnt_inf_out = 0
    cnt_finite_out = 0
    for r in results:
        inp = r.get('input')
        outv = r.get('output')
        err = r.get('error')
        if err:
            cnt_error += 1
        if isinstance(inp, list) and len(inp) == 0:
            cnt_empty_input += 1
        # output analysis
        if outv is None:
            # treated as error or null output
            pass
        else:
            # outv may be list or scalar
            def is_inf(x):
                try:
                    return math.isinf(float(x))
                except Exception:
                    return False
            def is_nan(x):
                try:
                    return math.isnan(float(x))
                except Exception:
                    return False
            any_nan = False
            any_inf = False
            any_finite = False
            if isinstance(outv, list):
                for x in outv:
                    if is_nan(x):
                        any_nan = True
                    elif is_inf(x):
                        any_inf = True
                    else:
                        any_finite = True
            else:
                if is_nan(outv):
                    any_nan = True
                elif is_inf(outv):
                    any_inf = True
                else:
                    any_finite = True
            if any_nan:
                cnt_nan_out += 1
            if any_inf:
                cnt_inf_out += 1
            if any_finite and not any_nan and not any_inf:
                cnt_finite_out += 1
    out[str(p)] = {
        'n': n,
        'errors': cnt_error,
        'empty_input': cnt_empty_input,
        'nan_out': cnt_nan_out,
        'inf_out': cnt_inf_out,
        'finite_out': cnt_finite_out,
    }
print(json.dumps(out, indent=2))
