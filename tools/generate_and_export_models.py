#!/usr/bin/env python3
"""
Generate small PyTorch models composed from operator sequences and export as TorchScript and ONNX.

Usage: python3 tools/generate_and_export_models.py --out models --max-len 3

This creates models/<name>.pt, models/<name>.onnx and models/<name>.meta.json
"""
import os
import json
import argparse
from itertools import combinations, permutations

def make_module_fn(ops, input_size=8):
    # produce a string name and a python callable that builds a torch.nn.Module
    name = '_'.join(ops)
    def builder():
        import torch
        import torch.nn as nn
        class OpModel(nn.Module):
            def __init__(self):
                super().__init__()
            def forward(self, x):
                # ensure shape (1, input_size)
                # For binary ops we split x into two halves
                out = x
                for op in ops:
                    if op == 'div':
                        a,b = out.split(out.shape[-1]//2, dim=-1)
                        out = a / (b + 1e-6)
                    elif op == 'sub':
                        a,b = out.split(out.shape[-1]//2, dim=-1)
                        out = a - b
                    elif op == 'pow':
                        a,b = out.split(out.shape[-1]//2, dim=-1)
                        out = torch.pow(a, torch.clamp(b, -20, 20))
                    elif op == 'log':
                        out = torch.log(torch.clamp(out, 1e-6))
                    elif op == 'exp':
                        out = torch.exp(out)
                    elif op == 'sigmoid':
                        out = torch.sigmoid(out)
                    elif op == 'softmax':
                        out = torch.softmax(out, dim=-1)
                    elif op == 'cossim':
                        a,b = out.split(out.shape[-1]//2, dim=-1)
                        an = a / (torch.norm(a, dim=-1, keepdim=True)+1e-6)
                        bn = b / (torch.norm(b, dim=-1, keepdim=True)+1e-6)
                        out = (an * bn).sum(dim=-1, keepdim=True)
                    else:
                        out = out
                return out
        return OpModel(), (1, input_size)
    return name, builder

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='models')
    parser.add_argument('--ops', nargs='*', default=['div','log','exp','pow','sigmoid','softmax','sub','cossim'])
    parser.add_argument('--max-len', type=int, default=2)
    parser.add_argument('--input-size', type=int, default=8)
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    import torch

    # build combinations (permutations of length up to max_len)
    sequences = []
    for L in range(1, args.max_len+1):
        for seq in permutations(args.ops, L):
            sequences.append(seq)

    # keep to reasonable number
    sequences = sequences[:50]

    metas = {}
    for seq in sequences:
        name = '_'.join(seq)
        model_name = f"model_{name}"
        try:
            mod, shape = make_module_fn(seq, args.input_size)[1]()
            mod.eval()
            # trace example input
            example = torch.randn(*shape)
            # save torchscript
            ts = torch.jit.trace(mod, example)
            ts_path = os.path.join(args.out, model_name + '.pt')
            ts.save(ts_path)
            # export ONNX
            onnx_path = os.path.join(args.out, model_name + '.onnx')
            torch.onnx.export(mod, example, onnx_path, opset_version=11, input_names=['input'], output_names=['output'])
            metas[model_name] = {'seq': seq, 'torchscript': ts_path, 'onnx': onnx_path, 'input_size': shape[-1]}
            print('exported', model_name)
        except Exception as e:
            print('skip', model_name, 'err', e)

    # write metas
    with open(os.path.join(args.out, 'models_meta.json'), 'w') as f:
        json.dump(metas, f, indent=2)
    print('done')

if __name__ == '__main__':
    main()
