#!/usr/bin/env python3
"""Generate Torch modules that are sequences of basic numeric operators and export TorchScript.

Creates models/generated/<name>.pt
"""
from pathlib import Path
import itertools
import torch
import torch.nn as nn

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'models' / 'generated'
OUT.mkdir(parents=True, exist_ok=True)

OPS = ['exp', 'log', 'pow2', 'div', 'sigmoid']


class OpSequence(nn.Module):
    def __init__(self, ops):
        super().__init__()
        self.ops = ops

    def forward(self, x):
        # expect x shape (N, D) or (D,) -> treat as (1,D)
        if x.dim() == 1:
            x = x.unsqueeze(0)
        out = x
        for op in self.ops:
            if op == 'exp':
                out = torch.exp(out)
            elif op == 'log':
                # promote small positives to avoid -inf on <=0
                out = torch.log(out)
            elif op == 'pow2':
                out = torch.pow(out, 2.0)
            elif op == 'div':
                # 1 / x to exercise divide-by-zero
                out = 1.0 / out
            elif op == 'sigmoid':
                out = torch.sigmoid(out)
            else:
                raise RuntimeError('unknown op ' + op)
        # return reduced scalar (mean) to keep outputs simple
        return out.mean(dim=1)


def name_for_ops(ops):
    return 'seq_' + '__'.join(ops)


def main():
    # generate all length-2 and length-3 combinations
    combos = []
    for L in (2, 3):
        for tup in itertools.product(OPS, repeat=L):
            combos.append(list(tup))

    # limit total to a reasonable number (avoid explosion)
    combos = combos[:50]

    for ops in combos:
        name = name_for_ops(ops)
        p = OUT / f'{name}.pt'
        if p.exists():
            print('exists', p)
            continue
        m = OpSequence(ops)
        m.eval()
        # example input
        example = torch.randn(1, 16)
        try:
            scripted = torch.jit.trace(m, example)
            scripted.save(str(p))
            print('wrote', p)
        except Exception as e:
            print('failed export', name, e)


if __name__ == '__main__':
    main()
