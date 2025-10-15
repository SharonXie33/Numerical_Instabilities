#!/usr/bin/env python3
"""Export TorchScript (or nn.Module) models to ONNX files.

Writes to models/onnx/<modelname>.onnx
"""
from pathlib import Path
import torch
import sys

BASE = Path(__file__).resolve().parents[1]
MODELS = BASE / 'models'
OUT = MODELS / 'onnx'
OUT.mkdir(parents=True, exist_ok=True)


def export_torchscript(pt_path: Path, out_path: Path):
    try:
        m = torch.jit.load(str(pt_path))
        m.eval()
        # create example input; try to infer expected dim via parameter shapes
        # Heuristics:
        # - conv weight: (out_channels, in_channels, kH, kW) -> example (1, in_channels, 16, 16)
        # - conv1d weight: (out_channels, in_channels, kW) -> example (1, in_channels, 64)
        # - linear weight: (out_features, in_features) -> example (1, in_features)
        # fallback to (1,16)
        example = None
        try:
            params = list(m.parameters())
            if params:
                for p in params:
                    if p.dim() == 4:
                        # conv2d weight
                        in_ch = int(p.shape[1])
                        example = torch.randn(1, in_ch, 16, 16)
                        break
                    if p.dim() == 3:
                        # conv1d / conv transpose-like
                        in_ch = int(p.shape[1])
                        example = torch.randn(1, in_ch, 64)
                        break
                    if p.dim() == 2:
                        in_dim = int(p.shape[1])
                        example = torch.randn(1, in_dim)
                        break
            if example is None:
                example = torch.randn(1, 16)
        except Exception:
            example = torch.randn(1, 16)
        torch.onnx.export(m, example, str(out_path), opset_version=13, do_constant_folding=True)
        return True, None
    except Exception as e:
        return False, str(e)


def main():
    # iterate models/*.pt and models/generated/*.pt
    candidates = list((MODELS).glob('*.pt')) + list((MODELS / 'generated').glob('*.pt'))
    for p in candidates:
        outp = OUT / (p.stem + '.onnx')
        ok, err = export_torchscript(p, outp)
        if ok:
            print('exported', outp)
        else:
            print('failed', p, err)


if __name__ == '__main__':
    main()
