#!/usr/bin/env python3
"""统一评测入口：支持 pytorch, torch_compile, onnx, tvm, tensorrt（缺少时跳过）

输出 summary.json 与 summary.csv（按 model × framework × dataset 聚合）。

示例：
  python runners/run_multi_framework.py --models models/auto_generated/models_meta.json --inputs "parsed_klee_inj_all/*/inputs.csv" --frameworks pytorch,onnx --out results/summary_multi

"""
import argparse
import glob
import json
import os
import csv
from typing import List


def load_csv_inputs(path):
    # return list of (testfile, list-of-floats)
    res = []
    with open(path) as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split(',', 1)
            if len(parts) != 2:
                continue
            tf, vals = parts
            vals_list = [v for v in vals.split(',') if v!='']
            arr = []
            for s in vals_list:
                s2 = s.strip()
                if s2.lower() == 'nan':
                    arr.append(float('nan'))
                elif s2.lower() in ('inf', '+inf'):
                    arr.append(float('inf'))
                elif s2.lower() == '-inf':
                    arr.append(float('-inf'))
                else:
                    try:
                        arr.append(float(s2))
                    except Exception:
                        try:
                            if s2.startswith('0x'):
                                arr.append(float(int(s2,16)))
                            else:
                                arr.append(float(s2))
                        except Exception:
                            arr.append(float('nan'))
            res.append((tf, arr))
    return res


def try_import(name):
    try:
        mod = __import__(name)
        return mod
    except Exception:
        return None


def run_pytorch(ts_path, inputs):
    import torch
    import numpy as np
    out = []
    try:
        mod = torch.jit.load(ts_path)
        mod.eval()
    except Exception as e:
        # cannot load
        for tf, arr in inputs:
            out.append({'testfile': tf, 'error': str(e)})
        return out

    for tf, arr in inputs:
        a = None
        try:
            a = torch.tensor([arr], dtype=torch.float32)
            with torch.no_grad():
                res = mod(a)
            # convert to python types when possible
            try:
                r = res.cpu().numpy().tolist()
            except Exception:
                try:
                    r = float(res)
                except Exception:
                    r = str(res)
            import math
            # stats
            def has_nan_inf(x):
                try:
                    import numpy as _np
                    arrx = _np.array(x)
                    return bool(_np.isnan(arrx).any()), bool(_np.isinf(arrx).any())
                except Exception:
                    return False, False

            nan, inf = has_nan_inf(r)
            out.append({'testfile': tf, 'output': r, 'has_nan': nan, 'has_inf': inf})
        except Exception as e:
            out.append({'testfile': tf, 'error': str(e)})
    return out


def run_torch_compile(ts_path, inputs):
    # try to compile the torchscript module (if torch.compile available)
    import torch
    mod = None
    try:
        mod = torch.jit.load(ts_path)
        mod.eval()
    except Exception as e:
        return [{'testfile': tf, 'error': f'load error: {e}'} for tf, _ in inputs]

    if not hasattr(torch, 'compile'):
        return [{'testfile': tf, 'error': 'torch.compile not available'} for tf, _ in inputs]

    try:
        compiled = torch.compile(mod)
    except Exception as e:
        return [{'testfile': tf, 'error': f'compile error: {e}'} for tf, _ in inputs]

    out = []
    for tf, arr in inputs:
        try:
            a = torch.tensor([arr], dtype=torch.float32)
            with torch.no_grad():
                res = compiled(a)
            try:
                r = res.cpu().numpy().tolist()
            except Exception:
                try:
                    r = float(res)
                except Exception:
                    r = str(res)
            import numpy as _np
            nan = bool(_np.isnan(_np.array(r)).any())
            inf = bool(_np.isinf(_np.array(r)).any())
            out.append({'testfile': tf, 'output': r, 'has_nan': nan, 'has_inf': inf})
        except Exception as e:
            out.append({'testfile': tf, 'error': str(e)})
    return out


def run_onnx(onnx_path, inputs):
    import onnxruntime as ort
    import numpy as np
    sess = ort.InferenceSession(onnx_path)
    out = []
    for tf, arr in inputs:
        a = np.array([arr], dtype=np.float32)
        try:
            res = sess.run(None, {'input': a})
            outv = [r.tolist() for r in res]
            has_nan = any((np.isnan(r).any() for r in res))
            has_inf = any((np.isinf(r).any() for r in res))
            out.append({'testfile': tf, 'output': outv, 'has_nan': bool(has_nan), 'has_inf': bool(has_inf)})
        except Exception as e:
            out.append({'testfile': tf, 'error': str(e)})
    return out


def run_tvm(onnx_path, inputs):
    # try import tvm; if not available, return skip
    try:
        import tvm
        from tvm import relay
        import numpy as np
    except Exception as e:
        return [{'testfile': tf, 'error': f'tvm not available: {e}'} for tf, _ in inputs]

    out = []
    try:
        import onnx
        model = onnx.load(onnx_path)
        shape_dict = {}
        mod, params = relay.frontend.from_onnx(model, shape=shape_dict)
        target = 'llvm'
        with tvm.transform.PassContext(opt_level=3):
            lib = relay.build(mod, target=target, params=params)
        from tvm.contrib import graph_executor
        dev = tvm.cpu()
        for tf, arr in inputs:
            a = np.array([arr], dtype=np.float32)
            m = graph_executor.GraphModule(lib['default'](dev))
            try:
                m.set_input('input', tvm.nd.array(a.astype('float32')))
                m.run()
                outv = m.get_output(0).asnumpy().tolist()
                import numpy as _np
                nan = bool(_np.isnan(_np.array(outv)).any())
                inf = bool(_np.isinf(_np.array(outv)).any())
                out.append({'testfile': tf, 'output': outv, 'has_nan': nan, 'has_inf': inf})
            except Exception as e:
                out.append({'testfile': tf, 'error': str(e)})
    except Exception as e:
        return [{'testfile': tf, 'error': f'tvm compile/load error: {e}'} for tf, _ in inputs]
    return out


def run_tensorrt(onnx_path, inputs):
    # best-effort: attempt to import tensorrt and use onnx parser; if unavailable skip
    try:
        import tensorrt as trt
    except Exception as e:
        return [{'testfile': tf, 'error': f'tensorrt not available: {e}'} for tf, _ in inputs]

    # building TensorRT engines is platform and CUDA dependent; skip actual engine build here
    return [{'testfile': tf, 'error': 'tensorrt support not implemented in this environment'} for tf, _ in inputs]


def aggregate_stats(results):
    # results: list of per-test dicts with keys 'testfile', maybe 'has_nan'/'has_inf' or 'error'
    total = len(results)
    num_nan = sum(1 for r in results if r.get('has_nan'))
    num_inf = sum(1 for r in results if r.get('has_inf'))
    num_err = sum(1 for r in results if 'error' in r)
    return {'total': total, 'num_nan': num_nan, 'num_inf': num_inf, 'num_error': num_err}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--models', required=True, help='models_meta.json')
    p.add_argument('--inputs', required=True, help='glob or directory to inputs.csv files')
    p.add_argument('--frameworks', default='pytorch,onnx', help='comma-separated frameworks to run')
    p.add_argument('--out', default='results/summary_multi', help='output directory')
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    metas = json.load(open(args.models))

    # expand inputs glob
    inputs_glob = args.inputs
    matches = glob.glob(inputs_glob)
    # if inputs is a directory, try to find */inputs.csv
    if os.path.isdir(args.inputs):
        matches = glob.glob(os.path.join(args.inputs, '*', 'inputs.csv'))

    datasets = {}
    for m in matches:
        # dataset name: parent dir name if present else basename
        ds_name = os.path.basename(os.path.dirname(m)) if os.path.basename(os.path.dirname(m)) else os.path.basename(m)
        datasets[ds_name] = load_csv_inputs(m)

    frameworks = [f.strip() for f in args.frameworks.split(',') if f.strip()]

    summary = []
    csv_rows = []

    for mname, meta in metas.items():
        for fw in frameworks:
            # choose path depending on framework
            for ds_name, inputs in datasets.items():
                results = []
                info = {'model': mname, 'framework': fw, 'dataset': ds_name}
                if fw == 'pytorch':
                    ts = meta.get('torchscript') or meta.get('torch') or meta.get('pt')
                    if not ts or not os.path.exists(ts):
                        info['note'] = 'torchscript missing'
                        results = [{'testfile': tf, 'error': 'torchscript missing'} for tf, _ in inputs]
                    else:
                        try:
                            results = run_pytorch(ts, inputs)
                        except Exception as e:
                            results = [{'testfile': tf, 'error': str(e)} for tf, _ in inputs]
                elif fw == 'torch_compile':
                    ts = meta.get('torchscript')
                    if not ts or not os.path.exists(ts):
                        results = [{'testfile': tf, 'error': 'torchscript missing'} for tf, _ in inputs]
                    else:
                        results = run_torch_compile(ts, inputs)
                elif fw == 'onnx':
                    onnxp = meta.get('onnx')
                    if not onnxp or not os.path.exists(onnxp):
                        results = [{'testfile': tf, 'error': 'onnx missing'} for tf, _ in inputs]
                    else:
                        results = run_onnx(onnxp, inputs)
                elif fw == 'tvm':
                    onnxp = meta.get('onnx')
                    if not onnxp or not os.path.exists(onnxp):
                        results = [{'testfile': tf, 'error': 'onnx missing'} for tf, _ in inputs]
                    else:
                        results = run_tvm(onnxp, inputs)
                elif fw == 'tensorrt':
                    onnxp = meta.get('onnx')
                    if not onnxp or not os.path.exists(onnxp):
                        results = [{'testfile': tf, 'error': 'onnx missing'} for tf, _ in inputs]
                    else:
                        results = run_tensorrt(onnxp, inputs)
                else:
                    results = [{'testfile': tf, 'error': f'unknown framework {fw}'} for tf, _ in inputs]

                stats = aggregate_stats(results)
                info.update(stats)
                # store sample results count (first 3 samples)
                info['sample'] = results[:3]
                summary.append(info)
                csv_rows.append([mname, fw, ds_name, stats['total'], stats['num_nan'], stats['num_inf'], stats['num_error']])

    # write json
    out_json = os.path.join(args.out, 'summary.json')
    with open(out_json, 'w') as f:
        json.dump(summary, f, indent=2)

    # write csv
    out_csv = os.path.join(args.out, 'summary.csv')
    with open(out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['model', 'framework', 'dataset', 'total', 'num_nan', 'num_inf', 'num_error'])
        for r in csv_rows:
            w.writerow(r)

    print('wrote', out_json, out_csv)


if __name__ == '__main__':
    main()
