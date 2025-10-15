#!/usr/bin/env python3
"""Run ONNX models via TVM on repro inputs and produce summary.json / summary.csv like the other runners.

This is a best-effort runner: if TVM is not installed it prints instructions and exits 1.
"""
import argparse
from pathlib import Path
import json
import csv
import numpy as np


def read_repro_input(path: Path):
    import numpy as np
    if path.suffix == '.npy':
        return np.load(str(path)).astype(np.float32)
    txt = path.read_text().strip()
    parts = [p for p in txt.replace('\n', ',').split(',') if p!='']
    vals = []
    for p in parts:
        try:
            vals.append(float(p))
        except Exception:
            lp = p.lower()
            if lp == 'nan':
                vals.append(np.nan)
            elif lp in ('inf','+inf'):
                vals.append(np.inf)
            elif lp == '-inf':
                vals.append(-np.inf)
    return np.array(vals, dtype=np.float32)


def summarize(rows, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    js = {'n': len(rows), 'results': rows}
    with open(outdir / 'summary.json', 'w') as f:
        json.dump(js, f, indent=2)
    with open(outdir / 'summary.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['repro_file','input_len','has_nan_in','has_inf_in','output','has_nan_out','has_inf_out','error'])
        for r in rows:
            inp = r.get('input')
            has_nan_in = bool(np.isnan(inp).any()) if inp is not None else ''
            has_inf_in = bool(np.isinf(inp).any()) if inp is not None else ''
            outv = r.get('output')
            has_nan_out = ''
            has_inf_out = ''
            if outv is not None:
                try:
                    arr = np.array(outv, dtype=float)
                    has_nan_out = bool(np.isnan(arr).any())
                    has_inf_out = bool(np.isinf(arr).any())
                except Exception:
                    pass
            w.writerow([r.get('repro_file'), len(inp) if inp is not None else 0, has_nan_in, has_inf_in, json.dumps(outv), has_nan_out, has_inf_out, r.get('error') or ''])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--onnx', required=True, help='input ONNX model to compile with TVM')
    p.add_argument('--repro', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()

    try:
        import onnx
        import tvm
        from tvm import relay
        import numpy as np
    except Exception as e:
        print('TVM not available or import failed:', e)
        print('To install TVM, see https://tvm.apache.org/docs/install/index.html')
        raise SystemExit(1)

    onnx_p = Path(args.onnx)
    repro = Path(args.repro)
    outdir = Path(args.out)

    onnx_model = onnx.load(str(onnx_p))
    shape_dict = {}
    # naive: assume first input is (1, N) when possible
    # TODO: improve shape inference from repros
    mod, params = relay.frontend.from_onnx(onnx_model, shape_dict)
    target = 'llvm'
    with tvm.transform.PassContext(opt_level=3):
        lib = relay.build(mod, target=target, params=params)

    # create runtime
    from tvm.contrib import graph_executor
    dev = tvm.cpu(0)
    module = graph_executor.GraphModule(lib['default'](dev))

    repro_files = sorted([q for q in repro.iterdir() if q.suffix in ('.npy', '.csv')])
    rows = []
    for rp in repro_files:
        try:
            arr = read_repro_input(rp)
        except Exception as e:
            rows.append({'repro_file': str(rp), 'input': None, 'output': None, 'error': 'read error: '+str(e)})
            continue
        x = arr
        if x.ndim == 1:
            x = x.reshape(1, -1)
        try:
            module.set_input(0, x.astype('float32'))
            module.run()
            out = module.get_output(0).asnumpy()
            rows.append({'repro_file': str(rp), 'input': arr.tolist(), 'output': out.tolist(), 'error': None})
        except Exception as e:
            rows.append({'repro_file': str(rp), 'input': arr.tolist(), 'output': None, 'error': str(e)})

    summarize(rows, outdir)
    print('Wrote', outdir / 'summary.json')


if __name__ == '__main__':
    main()
