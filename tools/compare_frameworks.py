#!/usr/bin/env python3
"""Compare framework outputs: for each run where both <model>_torch and <model>_onnx
exist under the same repro category, align per-repro-file outputs and report differences.

Produces runs/<model>_comparison/summary.json and summary.csv
"""
from pathlib import Path
import json
import numpy as np
import csv

BASE = Path(__file__).resolve().parents[1]
REPROS = BASE / 'results' / 'reproducers'


def load_summary(p: Path):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def norm_out(o):
    # normalize outputs for comparison
    if o is None:
        return ('null', None)
    try:
        a = np.array(o, dtype=float)
    except Exception:
        try:
            a = np.array([float(o)])
        except Exception:
            return ('other', str(o))
    if np.isnan(a).any():
        return ('nan', None)
    if np.isinf(a).any():
        # sign-aware
        s = np.sign(a[~np.isfinite(a)])[0] if a.size>0 else 0
        return ('inf', int(s))
    return ('finite', a)


def compare_runs(ts_json: Path, onnx_json: Path):
    ts = load_summary(ts_json)
    onx = load_summary(onnx_json)
    if ts is None or onx is None:
        return None
    ts_map = {Path(r['repro_file']).name: r for r in ts.get('results', [])}
    on_map = {Path(r['repro_file']).name: r for r in onx.get('results', [])}
    keys = sorted(set(ts_map.keys()) | set(on_map.keys()))
    rows = []
    stats = {'total':0,'match':0,'mismatch':0,'ts_error':0,'on_error':0,'ts_nan_only':0,'on_nan_only':0}
    for k in keys:
        ts_e = ts_map.get(k)
        on_e = on_map.get(k)
        stats['total'] += 1
        ts_err = ts_e.get('error') if ts_e else 'missing'
        on_err = on_e.get('error') if on_e else 'missing'
        if ts_err:
            stats['ts_error'] += 1
        if on_err:
            stats['on_error'] += 1
        ts_out = ts_e.get('output') if ts_e else None
        on_out = on_e.get('output') if on_e else None
        t_type, t_val = norm_out(ts_out)
        o_type, o_val = norm_out(on_out)
        equal = False
        reason = ''
        if t_type == o_type == 'finite':
            # compare numerically with tolerance
            a = t_val
            b = np.array(o_val, dtype=float)
            try:
                if a.shape == b.shape and np.allclose(a, b, atol=1e-6, rtol=1e-6):
                    equal = True
                else:
                    reason = 'numeric_diff'
            except Exception:
                reason = 'numeric_cmp_err'
        elif t_type == o_type:
            # both nan or both inf
            equal = True
        else:
            reason = f'ts={t_type},on={o_type}'
            if t_type == 'nan' and o_type != 'nan':
                stats['ts_nan_only'] += 1
            if o_type == 'nan' and t_type != 'nan':
                stats['on_nan_only'] += 1

        if equal:
            stats['match'] += 1
        else:
            stats['mismatch'] += 1

        rows.append({'repro_file': k, 'ts_error': ts_err, 'on_error': on_err, 'ts_type': t_type, 'on_type': o_type, 'equal': equal, 'reason': reason})

    return rows, stats


def main():
    # walk repro categories
    for repro_cat in sorted(REPROS.glob('**/targeted/*')):
        # find runs subdirs
        runs_dir = repro_cat / 'runs'
        if not runs_dir.exists():
            continue
        # map model base names
        # look for *_torch and *_onnx pairs
        entries = {}
        for r in runs_dir.iterdir():
            if not r.is_dir():
                continue
            name = r.name
            if name.endswith('_torch'):
                base = name[:-6]
                entries.setdefault(base, {})['torch'] = r / 'summary.json'
            if name.endswith('_onnx'):
                base = name[:-5]
                entries.setdefault(base, {})['onnx'] = r / 'summary.json'

        for base, v in entries.items():
            if 'torch' in v and 'onnx' in v:
                outdir = runs_dir / (base + '_comparison')
                outdir.mkdir(parents=True, exist_ok=True)
                rows, stats = compare_runs(v['torch'], v['onnx'])
                if rows is None:
                    continue
                with open(outdir / 'summary.json', 'w') as f:
                    json.dump({'stats': stats, 'n': len(rows)}, f, indent=2)
                with open(outdir / 'summary.csv', 'w', newline='') as f:
                    w = csv.writer(f)
                    w.writerow(['repro_file','ts_error','on_error','ts_type','on_type','equal','reason'])
                    for r in rows:
                        w.writerow([r['repro_file'], r['ts_error'] or '', r['on_error'] or '', r['ts_type'], r['on_type'], r['equal'], r['reason']])
                print('wrote comparison for', base, '->', outdir)


if __name__ == '__main__':
    main()
