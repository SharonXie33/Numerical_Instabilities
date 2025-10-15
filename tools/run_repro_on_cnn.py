#!/usr/bin/env python3
"""Run 1D repro inputs by reshaping to image tensors for cnn_bn.pt

This script reuses read_repro_input from run_repro_on_model.py by importing it.
It maps a flat vector into (1,3,16,16) by pad/truncate and then calls the torchscript model.

Usage:
  python tools/run_repro_on_cnn.py --repro <repro_dir> --model-path models/cnn_bn.pt --out <out_dir>
"""
import argparse
import json
from pathlib import Path
import numpy as np

# import helper from run_repro_on_model
import sys
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from tools.run_repro_on_model import read_repro_input


def load_torchscript_model(path: str):
    import torch
    m = torch.jit.load(path)
    m.eval()
    return m


def run_cnn_model(model, arr: np.ndarray):
    import torch
    # target shape (1,3,16,16) -> total elements 768
    target = 1 * 3 * 16 * 16
    v = np.ravel(arr).astype(np.float32)
    if v.size < target:
        nv = np.zeros(target, dtype=np.float32)
        nv[:v.size] = v
    else:
        nv = v[:target]
    t = torch.from_numpy(nv).view(1, 3, 16, 16)
    with torch.no_grad():
        out = model(t)
    if isinstance(out, torch.Tensor):
        return out.cpu().numpy().tolist(), None
    return out, None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repro', required=True)
    p.add_argument('--model-path', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()

    repro = Path(args.repro)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    repro_files = sorted([p for p in repro.iterdir() if p.suffix in ('.npy', '.csv')])
    model = load_torchscript_model(args.model_path)
    rows = []
    for rp in repro_files:
        try:
            arr = read_repro_input(rp)
        except Exception as e:
            rows.append({'repro_file': str(rp), 'input': None, 'output': None, 'error': 'read error: '+str(e)})
            continue
        out, err = run_cnn_model(model, arr)
        rows.append({'repro_file': str(rp), 'input': arr.tolist(), 'output': out, 'error': err})

    js_p = outdir / 'summary.json'
    with open(js_p, 'w') as f:
        json.dump({'n': len(rows), 'results': rows}, f, indent=2)
    print('Wrote', js_p)


if __name__ == '__main__':
    main()
