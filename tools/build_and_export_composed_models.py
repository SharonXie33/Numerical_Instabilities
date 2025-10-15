#!/usr/bin/env python3
"""自动组合操作并导出 TorchScript + ONNX 模型

用法示例:
  python tools/build_and_export_composed_models.py --ops add,sub,div,exp,log,pow,sigmoid,softmax --combo-len 2 --out models/auto_generated --min-count 10

脚本会在指定输出目录生成模型文件（.pt 和 .onnx）并写入 models_meta.json。
"""
import argparse
import itertools
import json
import os
from typing import List

import torch
import torch.nn as nn
import torch.nn.functional as F


OP_NAMES = [
    "add",
    "sub",
    "div",
    "exp",
    "log",
    "pow",
    "sigmoid",
    "softmax",
    "cossim",
]


class ComposedModule(nn.Module):
    def __init__(self, ops: List[str]):
        super().__init__()
        self.ops = ops

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = x
        eps = 1e-6
        for op in self.ops:
            if op == "add":
                y = y + 1.0
            elif op == "sub":
                y = y - 1.0
            elif op == "div":
                # keep shape; avoid division by zero
                y = y / (y + eps)
            elif op == "exp":
                y = torch.exp(y)
            elif op == "log":
                y = torch.log(torch.abs(y) + eps)
            elif op == "pow":
                y = torch.pow(y, 2.0)
            elif op == "sigmoid":
                y = torch.sigmoid(y)
            elif op == "softmax":
                # softmax along last dim (assume shape [B, N])
                y = torch.softmax(y, dim=1)
            elif op == "cossim":
                # scale by cosine similarity to a constant vector of ones
                v = torch.ones_like(y)
                cs = F.cosine_similarity(y, v, dim=1, eps=eps)  # shape [B]
                y = y * cs.unsqueeze(1)
            else:
                # unknown op: passthrough
                pass
        return y


def make_sequences(ops: List[str], combo_len: int, min_count: int) -> List[List[str]]:
    # Generate product sequences of exactly combo_len, but if not enough sequences
    # try lengths 1..combo_len and stop when >= min_count
    sequences = []
    for L in range(1, combo_len + 1):
        for seq in itertools.product(ops, repeat=L):
            sequences.append(list(seq))
            if len(sequences) >= min_count:
                return sequences
    return sequences


def export_model(mod: nn.Module, example_input: torch.Tensor, out_base: str, name: str):
    os.makedirs(out_base, exist_ok=True)
    # TorchScript
    try:
        ts = torch.jit.trace(mod, example_input)
        ts_path = os.path.join(out_base, f"{name}.pt")
        ts.save(ts_path)
    except Exception as e:
        print(f"torchscript export failed for {name}: {e}")
        ts_path = None

    # ONNX
    onnx_path = os.path.join(out_base, f"{name}.onnx")
    try:
        # export with opset 11 for compatibility
        torch.onnx.export(mod, example_input, onnx_path, opset_version=11, input_names=["input"], output_names=["output"])
    except Exception as e:
        print(f"onnx export failed for {name}: {e}")
        onnx_path = None

    return ts_path, onnx_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ops", default=",".join(OP_NAMES), help="comma-separated ops to combine")
    parser.add_argument("--combo-len", type=int, default=2, help="maximum composition length")
    parser.add_argument("--out", default="models/auto_generated", help="output directory for models")
    parser.add_argument("--min-count", type=int, default=10, help="minimum number of models to generate")
    parser.add_argument("--example-shape", default="1,16", help="example input shape as comma-separated dims, e.g. 1,16")
    args = parser.parse_args()

    ops = [o.strip() for o in args.ops.split(',') if o.strip()]
    combo_len = max(1, args.combo_len)
    out_dir = args.out
    min_count = max(1, args.min_count)

    # validate ops
    for o in ops:
        if o not in OP_NAMES:
            raise SystemExit(f"unknown op '{o}'. allowed: {OP_NAMES}")

    sequences = make_sequences(ops, combo_len, min_count)
    print(f"Planning to generate {len(sequences)} models into {out_dir}")

    os.makedirs(out_dir, exist_ok=True)
    meta = {}

    # parse example shape
    shape = tuple(int(x) for x in args.example_shape.split(',') if x)
    example = torch.randn(shape)

    count = 0
    for seq in sequences:
        name = "_".join(["model"] + seq)
        safe_name = name.replace('/', '_')
        model_dir = out_dir

        mod = ComposedModule(seq)
        mod.eval()

        print(f"exporting {safe_name} ops={seq} ...")
        ts_path, onnx_path = export_model(mod, example, model_dir, safe_name)
        meta[safe_name] = {
            "ops": seq,
            "torchscript": ts_path,
            "onnx": onnx_path,
        }
        count += 1

    meta_path = os.path.join(out_dir, "models_meta.json")
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"done: {count} models written to {out_dir}")
    print(f"models_meta.json written to {meta_path}")


if __name__ == '__main__':
    main()
