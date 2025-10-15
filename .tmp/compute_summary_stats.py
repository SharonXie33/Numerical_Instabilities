import json
import numpy as np
from pathlib import Path
import csv
import math

BASE = Path('/Users/xieyushan/Documents/code/Numerical_instabilities')
repro_base = BASE / 'results' / 'reproducers'


def load_summary(run_summary_path: Path):
    try:
        return json.loads(run_summary_path.read_text())
    except Exception:
        return None


def to_array(v):
    # convert nested lists or scalars to 1D numpy float array
    try:
        a = np.array(v, dtype=float)
    except Exception:
        try:
            a = np.array([float(v)])
        except Exception:
            a = np.array([np.nan], dtype=float)
    return a.flatten()


def compare_outputs(a, b, rtol=1e-5, atol=1e-8):
    # a and b are 1D numpy arrays
    if a.size == 0 and b.size == 0:
        return {'both_empty': True, 'allclose': True, 'max_abs': 0.0, 'max_rel': 0.0}
    if a.size != b.size:
        # try to compare flattened and align to min length
        n = min(a.size, b.size)
        a2 = a[:n]
        b2 = b[:n]
    else:
        a2 = a
        b2 = b
    # treat NaN/Inf explicitly
    if np.isnan(a2).any() or np.isnan(b2).any():
        return {'both_empty': False, 'allclose': False, 'max_abs': float('nan'), 'max_rel': float('nan'), 'nan_present': True}
    if np.isinf(a2).any() or np.isinf(b2).any():
        return {'both_empty': False, 'allclose': False, 'max_abs': float('inf'), 'max_rel': float('inf'), 'inf_present': True}
    absdiff = np.abs(a2 - b2)
    with np.errstate(divide='ignore', invalid='ignore'):
        rel = absdiff / np.maximum(np.abs(b2), atol)
    max_abs = float(np.max(absdiff)) if absdiff.size else 0.0
    max_rel = float(np.nanmax(rel)) if rel.size else 0.0
    allclose = bool(np.allclose(a2, b2, rtol=rtol, atol=atol, equal_nan=False))
    return {'both_empty': False, 'allclose': allclose, 'max_abs': max_abs, 'max_rel': max_rel}


def discover_run_summaries(base: Path):
    # returns mapping: category_path -> { run_name -> summary.json path }
    runs = {}
    for summary in sorted(base.glob('**/runs/*/summary.json')):
        run_dir = summary.parent
        # category is two levels up from runs dir (results/reproducers/.../<category>/runs)
        # we will take the path up to the category folder to group runs
        # e.g., results/reproducers/targeted/denom_near_zero/runs/<model>_
        category = run_dir.parent
        key = str(category.relative_to(base))
        runs.setdefault(key, {})[run_dir.name] = summary
    return runs


def aggregate_and_compare():
    runs = discover_run_summaries(repro_base)
    outdir = BASE / '.tmp'
    outdir.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    cross_summary = {}

    for category, mapping in runs.items():
        # group by model base name (strip framework suffixes like _torch, _onnx, _tvm, _tensorrt)
        groups = {}
        for run_name, summary_path in mapping.items():
            # try to find suffix
            parts = run_name.rsplit('_', 1)
            if len(parts) == 2 and parts[1] in ('torch', 'onnx', 'tvm', 'tensorrt'):
                base_name, fw = parts[0], parts[1]
            else:
                # unknown suffix -> keep full name and mark framework as 'unknown'
                base_name, fw = run_name, 'unknown'
            groups.setdefault(base_name, {})[fw] = summary_path

        for model_base, fw_map in groups.items():
            entry = {'category': category, 'model': model_base, 'frameworks': list(fw_map.keys())}
            # load summaries
            summaries = {fw: load_summary(path) for fw, path in fw_map.items()}
            # build repro_file -> entry mapping per framework
            per_fw_map = {}
            for fw, s in summaries.items():
                if not s:
                    per_fw_map[fw] = {}
                    continue
                d = {}
                for r in s.get('results', []):
                    d[r.get('repro_file')] = r
                per_fw_map[fw] = d

            # if we have torch and onnx, compare
            stats = {'n_inputs': 0}
            if 'torch' in per_fw_map and 'onnx' in per_fw_map:
                torch_map = per_fw_map['torch']
                onnx_map = per_fw_map['onnx']
                # compare intersection of repro files
                keys = set(torch_map.keys()) & set(onnx_map.keys())
                stats['n_inputs'] = len(keys)
                nan_t = inf_t = nan_o = inf_o = 0
                mismatch = 0
                max_abs = 0.0
                max_rel = 0.0
                abs_sum = 0.0
                for k in sorted(keys):
                    a_entry = torch_map[k]
                    b_entry = onnx_map[k]
                    a_out = a_entry.get('output')
                    b_out = b_entry.get('output')
                    a_err = a_entry.get('error')
                    b_err = b_entry.get('error')
                    if a_err:
                        # count as output null for torch
                        pass
                    A = to_array(a_out) if a_out is not None else np.array([np.nan])
                    B = to_array(b_out) if b_out is not None else np.array([np.nan])
                    if np.isnan(A).any():
                        nan_t += 1
                    if np.isnan(B).any():
                        nan_o += 1
                    if np.isinf(A).any():
                        inf_t += 1
                    if np.isinf(B).any():
                        inf_o += 1
                    cmp = compare_outputs(A, B)
                    if cmp.get('nan_present') or cmp.get('inf_present'):
                        mismatch += 1
                    else:
                        if not cmp.get('allclose', False):
                            mismatch += 1
                    if not math.isnan(cmp.get('max_abs', float('nan'))):
                        max_abs = max(max_abs, cmp.get('max_abs', 0.0) or 0.0)
                    if not math.isnan(cmp.get('max_rel', float('nan'))):
                        max_rel = max(max_rel, cmp.get('max_rel', 0.0) or 0.0)
                    abs_sum += (cmp.get('max_abs') or 0.0)

                mean_abs = (abs_sum / stats['n_inputs']) if stats['n_inputs'] else 0.0
                stats.update({'nan_torch': nan_t, 'nan_onnx': nan_o, 'inf_torch': inf_t, 'inf_onnx': inf_o, 'mismatch': mismatch, 'max_abs': max_abs, 'max_rel': max_rel, 'mean_abs': mean_abs})
            else:
                # no pair to compare; record counts from the single framework if present
                total = 0
                fstats = {}
                for fw, fmap in per_fw_map.items():
                    cnt_nan = cnt_inf = cnt_out = 0
                    for v in fmap.values():
                        outv = v.get('output')
                        if outv is None:
                            continue
                        arr = to_array(outv)
                        if np.isnan(arr).any():
                            cnt_nan += 1
                        elif np.isinf(arr).any():
                            cnt_inf += 1
                        else:
                            cnt_out += 1
                    fstats[fw] = {'nan': cnt_nan, 'inf': cnt_inf, 'finite': cnt_out}
                    total += len(fmap)
                stats.update({'n_inputs': total, 'per_framework_stats': fstats})

            cross_summary_key = f"{category}||{model_base}"
            cross_summary[cross_summary_key] = {'category': category, 'model': model_base, 'frameworks': list(fw_map.keys()), 'stats': stats}

            # append CSV row
            summary_rows.append([category, model_base, '|'.join(sorted(fw_map.keys())), stats.get('n_inputs', 0), stats.get('nan_torch', 0), stats.get('nan_onnx', 0), stats.get('inf_torch', 0), stats.get('inf_onnx', 0), stats.get('mismatch', 0), stats.get('max_abs', 0.0), stats.get('max_rel', 0.0)])

    # write JSON
    json_p = outdir / 'cross_framework_summary.json'
    json_p.write_text(json.dumps(cross_summary, indent=2))

    # write CSV
    csv_p = outdir / 'cross_framework_summary.csv'
    with open(csv_p, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['category', 'model', 'frameworks', 'n_inputs', 'nan_torch', 'nan_onnx', 'inf_torch', 'inf_onnx', 'mismatch', 'max_abs', 'max_rel'])
        for r in summary_rows:
            w.writerow(r)

    # write simple markdown report
    md_p = outdir / 'cross_framework_report.md'
    with open(md_p, 'w') as f:
        f.write('# Cross-framework comparison report\n\n')
        f.write(f'Total models compared: {len(summary_rows)}\n\n')
        f.write('Top mismatches (by mismatch count):\n\n')
        # sort by mismatch desc
        sorted_rows = sorted(summary_rows, key=lambda x: int(x[8] or 0), reverse=True)
        for r in sorted_rows[:20]:
            f.write(f'- {r[0]}/{r[1]} frameworks={r[2]} n_inputs={r[3]} mismatches={r[8]} max_abs={r[9]} max_rel={r[10]}\n')

    # optional plotting of mismatch rates per model
    try:
        import matplotlib.pyplot as plt
        labels = [f"{r[0]}/{r[1]}" for r in summary_rows]
        mism = [int(r[8] or 0) / (int(r[3]) or 1) for r in summary_rows]
        if labels and mism:
            plt.figure(figsize=(max(8, len(labels)*0.4), 6))
            plt.bar(labels, mism)
            plt.xticks(rotation=90)
            plt.ylabel('mismatch_rate')
            plt.title('Cross-framework mismatch rate per model')
            plt.tight_layout()
            plot_p = outdir / 'mismatch_rates.png'
            plt.savefig(plot_p)
            print('Wrote plot', plot_p)
    except Exception as e:
        print('matplotlib not available or plotting failed:', e)

    print('Wrote', json_p, csv_p, md_p)


if __name__ == '__main__':
    aggregate_and_compare()

