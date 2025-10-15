#!/usr/bin/env python3
"""Extract top-K repro inputs that produced NaN/Inf or errors from run summary.json files.

Creates per-run folders: <run_dir>/mini_repros/topk_<K>/ and copies the original repro files there.
Selection priority: entries with error != None, then NaN outputs, then Inf outputs.
"""
import json
from pathlib import Path
import shutil
import numpy as np

BASE = Path('/Users/xieyushan/Documents/code/Numerical_instabilities')
repro_base = BASE / 'results' / 'reproducers'
files = sorted(repro_base.glob('**/runs/*/summary.json'))

K = 5

for p in files:
    try:
        data = json.loads(p.read_text())
    except Exception:
        continue
    res = data.get('results', [])
    # build priority list
    scored = []
    for idx, entry in enumerate(res):
        score = 0
        err = entry.get('error')
        outv = entry.get('output')
        if err:
            score += 100
        if outv is None:
            score += 50
        else:
            try:
                arr = np.array(outv, dtype=float)
                if np.isnan(arr).any():
                    score += 20
                if np.isinf(arr).any():
                    score += 10
            except Exception:
                score += 5
        if score > 0:
            scored.append((score, idx, entry))
    if not scored:
        continue
    scored.sort(reverse=True)
    topk = scored[:K]
    run_dir = p.parent
    target_dir = run_dir / 'mini_repros' / f'topk_{K}'
    target_dir.mkdir(parents=True, exist_ok=True)
    for sc, idx, entry in topk:
        repro_path = entry.get('repro_file')
        if not repro_path:
            continue
        rp = Path(repro_path)
        if not rp.exists():
            # sometimes repro_file is relative to the run dir
            cand = run_dir.parent.parent / rp.name
            if cand.exists():
                rp = cand
        if rp.exists():
            try:
                shutil.copy2(rp, target_dir / rp.name)
            except Exception:
                pass

print('done')
