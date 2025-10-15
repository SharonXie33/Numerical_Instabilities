#!/usr/bin/env python3
"""Orchestrate: generate operator combos, export ONNX, run TorchScript and ONNXRuntime on repro inputs.

Produces per-framework run directories under results/reproducers/.../runs/<model>_(torch|onnx)/
"""
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parents[1]
TOOLS = BASE / 'tools'
MODELS_GEN = BASE / 'models' / 'generated'


def run_cmd(cmd):
    print('RUN:', ' '.join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout)
    return p.returncode


def main():
    # 1) generate operator combination torchscript models
    run_cmd([sys.executable, str(TOOLS / 'generate_operator_combinations.py')])
    # 2) export to onnx
    run_cmd([sys.executable, str(TOOLS / 'export_models_to_onnx.py')])

    # pick a small subset of models to smoke-test: first 4 generated
    gen = sorted(MODELS_GEN.glob('*.pt'))
    if not gen:
        print('no generated models')
        return
    gen = gen[:4]

    # pick a sample repro category
    repro_base = BASE / 'results' / 'reproducers' / 'targeted' / 'denom_near_zero'
    for p in gen:
        name = p.stem
        # run TorchScript model
        out_ts = BASE / 'results' / 'reproducers' / 'targeted' / 'denom_near_zero' / 'runs' / (name + '_torch')
        out_ts.parent.mkdir(parents=True, exist_ok=True)
        run_cmd([sys.executable, str(TOOLS / 'run_repro_on_model.py'), '--repro', str(repro_base), '--model', 'torchscript', '--model-path', str(p), '--out', str(out_ts)])
        # run ONNX
        onnx_file = BASE / 'models' / 'onnx' / (name + '.onnx')
        if onnx_file.exists():
            out_on = BASE / 'results' / 'reproducers' / 'targeted' / 'denom_near_zero' / 'runs' / (name + '_onnx')
            run_cmd([sys.executable, str(TOOLS / 'run_onnx_on_repro.py'), '--onnx', str(onnx_file), '--repro', str(repro_base), '--out', str(out_on)])
        else:
            print('no onnx for', name)


if __name__ == '__main__':
    main()
