#!/usr/bin/env python3
"""
Run ONNX models on parsed inputs and collect outputs/stats.

Usage: python3 tools/run_onnx_evaluator.py --models models/models_meta.json --inputs parsed_klee_inj_all --out results/models_eval
"""
import os
import argparse
import json
import glob

def load_inputs(input_dir):
    # find any inputs.csv under input_dir
    data = {}
    for p in glob.glob(os.path.join(input_dir, '*', 'inputs.csv')):
        name = os.path.basename(os.path.dirname(p))
        data[name] = []
        with open(p) as f:
            next(f)
            for line in f:
                tf, vals = line.strip().split(',', 1)
                # parse values into list of floats (allow nan/inf)
                arr = [float(x) if x not in ('nan','inf','-inf') else float('nan') if x=='nan' else float('inf') if x=='inf' else float('-inf') for x in vals.split(',')]
                data[name].append((tf, arr))
    return data

def run_onnx(onnx_path, inputs, out_file):
    import onnxruntime as ort
    import numpy as np
    sess = ort.InferenceSession(onnx_path)
    out = {'model': os.path.basename(onnx_path), 'results': []}
    for tf, arr in inputs:
        a = np.array([arr], dtype=np.float32)
        try:
            res = sess.run(None, {'input': a})
            outv = [r.tolist() for r in res]
            has_nan = any((np.isnan(r).any() for r in res))
            has_inf = any((np.isinf(r).any() for r in res))
        except Exception as e:
            outv = str(e)
            has_nan = False
            has_inf = False
        out['results'].append({'testfile': tf, 'input': arr, 'output': outv, 'stats': {'has_nan': bool(has_nan), 'has_inf': bool(has_inf)}})
    with open(out_file, 'w') as f:
        json.dump(out, f, indent=2)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--models', required=True)
    p.add_argument('--inputs', required=True)
    p.add_argument('--out', default='results/models_eval')
    args = p.parse_args()
    os.makedirs(args.out, exist_ok=True)
    metas = json.load(open(args.models))
    inputs = load_inputs(args.inputs)
    for mname, meta in metas.items():
        onnx = meta.get('onnx')
        if not onnx or not os.path.exists(onnx):
            continue
        # choose inputs dataset by name mapping; try to run all input sets
        for ds_name, ds in inputs.items():
            outf = os.path.join(args.out, f"{mname}__{ds_name}.json")
            print('running', onnx, 'on', ds_name, '->', outf)
            try:
                run_onnx(onnx, ds, outf)
            except Exception as e:
                print('error running', onnx, e)

if __name__ == '__main__':
    main()
