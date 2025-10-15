#!/usr/bin/env python3
"""Build and export small PyTorch models as TorchScript for repro testing.

Creates models and writes them to `models/<name>.pt`.

Models:
 - small_classifier.pt   : Linear -> ReLU -> Linear (outputs scalar)
 - small_layernorm.pt    : LayerNorm-only module for vector inputs
 - tiny_attention.pt     : Single-head attention-like module (queries==keys==values from same vector)

This script requires PyTorch to be installed in the active Python environment.
"""
import os
from pathlib import Path
import sys


def build_and_export():
    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
    except Exception as e:
        print('PyTorch import failed:', e)
        sys.exit(2)

    out_dir = Path(__file__).resolve().parents[1] / 'models'
    out_dir.mkdir(parents=True, exist_ok=True)

    # small classifier
    class SmallClassifier(nn.Module):
        def __init__(self, dim=16, hidden=32):
            super().__init__()
            self.fc1 = nn.Linear(dim, hidden)
            self.fc2 = nn.Linear(hidden, 1)

        def forward(self, x):
            # x: (N, dim)
            h = F.relu(self.fc1(x))
            y = self.fc2(h)
            return y.squeeze(-1)

    # small layernorm module
    class SmallLayerNorm(nn.Module):
        def __init__(self, dim=16, eps=1e-5):
            super().__init__()
            self.ln = nn.LayerNorm(dim, eps=eps)

        def forward(self, x):
            # x: (N, dim)
            return self.ln(x)

    # tiny attention
    class TinyAttention(nn.Module):
        def __init__(self, dim=16):
            super().__init__()
            self.q = nn.Linear(dim, dim, bias=False)
            self.k = nn.Linear(dim, dim, bias=False)
            self.v = nn.Linear(dim, dim, bias=False)

        def forward(self, x):
            # x: (N, dim)  -> treat N as sequence length (we'll accept (1, dim) as single seq)
            # produce pooled output per sequence
            Q = self.q(x)  # (N, dim)
            K = self.k(x)
            V = self.v(x)
            # scaled dot-product
            scores = torch.matmul(Q, K.transpose(0,1)) / (x.shape[-1] ** 0.5)
            weights = torch.softmax(scores, dim=-1)
            out = torch.matmul(weights, V)
            # pool to vector (mean over seq)
            return out.mean(dim=0)

    # build and export function
    def export_model(mod, name, example_input):
        try:
            scripted = torch.jit.script(mod)
        except Exception:
            scripted = torch.jit.trace(mod, example_input)
        p = out_dir / f'{name}.pt'
        scripted.save(str(p))
        print('Wrote', p)

    # create and export
    dim = 16
    # classifier: expect input (1,dim)
    cls = SmallClassifier(dim=dim, hidden=32)
    export_model(cls, 'small_classifier', torch.randn(1, dim))

    ln = SmallLayerNorm(dim=dim)
    export_model(ln, 'small_layernorm', torch.randn(1, dim))

    attn = TinyAttention(dim=dim)
    # for attention, example input is a small sequence (e.g., 3 x dim)
    export_model(attn, 'tiny_attention', torch.randn(3, dim))

    # ---- additional models for numeric-instability triage ----
    # Softmax scorer: applies a linear layer then softmax
    class SoftmaxScorer(nn.Module):
        def __init__(self, dim=16, classes=10):
            super().__init__()
            self.fc = nn.Linear(dim, classes)

        def forward(self, x):
            # x: (N, dim)
            logits = self.fc(x)
            return torch.softmax(logits, dim=-1)

    # Division/log/exp pipeline to provoke divide-by-zero/log/exp issues
    class DivLogExp(nn.Module):
        def __init__(self, dim=16):
            super().__init__()
            self.scale = nn.Parameter(torch.ones(dim))

        def forward(self, x):
            # x: (N, dim)
            # compute x / scale, then log, then exp
            y = x / (self.scale + 1e-12)
            # introduce potential negative/zero values
            y = torch.log(torch.abs(y) + 1e-12)
            return torch.exp(y)

    # explicit LayerNorm with name to distinguish
    class LayerNorm16(nn.Module):
        def __init__(self, dim=16, eps=1e-5):
            super().__init__()
            self.ln = nn.LayerNorm(dim, eps=eps)

        def forward(self, x):
            return self.ln(x)

    # Scaled Dot-Product Attention with explicit scaling param
    class ScaledDotProductAttention(nn.Module):
        def __init__(self, dim=16, scale=None):
            super().__init__()
            self.q = nn.Linear(dim, dim, bias=False)
            self.k = nn.Linear(dim, dim, bias=False)
            self.v = nn.Linear(dim, dim, bias=False)
            if scale is None:
                self.scale = float(dim) ** 0.5
            else:
                self.scale = float(scale)

        def forward(self, x):
            # x: (N, dim)
            Q = self.q(x)
            K = self.k(x)
            V = self.v(x)
            scores = torch.matmul(Q, K.transpose(0,1)) / (self.scale + 1e-12)
            weights = torch.softmax(scores, dim=-1)
            out = torch.matmul(weights, V)
            return out.mean(dim=0)

    # export the additional models
    sm = SoftmaxScorer(dim=dim, classes=10)
    export_model(sm, 'softmax_scorer', torch.randn(1, dim))

    dle = DivLogExp(dim=dim)
    export_model(dle, 'div_log_exp', torch.randn(1, dim))

    ln16 = LayerNorm16(dim=dim)
    export_model(ln16, 'layernorm16', torch.randn(1, dim))

    sdp = ScaledDotProductAttention(dim=dim)
    export_model(sdp, 'scaled_dotprod_attention', torch.randn(3, dim))

    # ---- basic operator micro-models ----
    class ExpOp(nn.Module):
        def __init__(self):
            super().__init__()

        def forward(self, x):
            # x: (N, dim) or (dim,)
            return torch.exp(x)

    class LogOp(nn.Module):
        def __init__(self):
            super().__init__()

        def forward(self, x):
            return torch.log(x)

    class PowOp(nn.Module):
        def __init__(self):
            super().__init__()

        def forward(self, x):
            # interpret x as pairwise (a,b) by splitting in half when possible
            if x.dim() == 1 and x.numel() % 2 == 0:
                mid = x.numel() // 2
                a = x[:mid]
                b = x[mid:]
                return torch.pow(a, b)
            # fallback: elementwise square
            return torch.pow(x, 2.0)

    class DivOp(nn.Module):
        def __init__(self):
            super().__init__()

        def forward(self, x):
            # if even-length vector, treat as (a,b) split; else reciprocal
            if x.dim() == 1 and x.numel() % 2 == 0:
                mid = x.numel() // 2
                a = x[:mid]
                b = x[mid:]
                return a / (b + 0.0)
            return x / (x + 1e-12)

    class SigmoidOp(nn.Module):
        def __init__(self):
            super().__init__()

        def forward(self, x):
            return torch.sigmoid(x)

    # export basic ops
    export_model(ExpOp(), 'op_exp', torch.randn(1, dim))
    export_model(LogOp(), 'op_log', torch.abs(torch.randn(1, dim)))
    export_model(PowOp(), 'op_pow', torch.randn(1, dim * 2))
    export_model(DivOp(), 'op_div', torch.randn(1, dim * 2))
    export_model(SigmoidOp(), 'op_sigmoid', torch.randn(1, dim))

    # ---- CNN + BatchNorm micro-model ----
    class SmallCNNBN(nn.Module):
        def __init__(self, in_ch=3, out_ch=8):
            super().__init__()
            # small conv stack
            self.conv1 = nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1)
            self.bn1 = nn.BatchNorm2d(out_ch)
            self.conv2 = nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1)
            self.bn2 = nn.BatchNorm2d(out_ch)
            self.pool = nn.AdaptiveAvgPool2d((1,1))

        def forward(self, x):
            # x: (B, C, H, W)
            h = F.relu(self.bn1(self.conv1(x)))
            h = F.relu(self.bn2(self.conv2(h)))
            p = self.pool(h)
            return p.view(p.size(0), -1)

    # export cnn model: example input (1,3,16,16)
    cnn = SmallCNNBN(in_ch=3, out_ch=8)
    export_model(cnn, 'cnn_bn', torch.randn(1, 3, 16, 16))

    # ---- CosineSimilarity micro-model ----
    class CosineSimilarityModel(nn.Module):
        def __init__(self, dim=16):
            super().__init__()
            self.dim = dim

        def forward(self, x):
            # x: 1D vector or (N, ) ; interpret as concatenated [a|b]
            # ensure we have 2*dim elements by pad/truncate
            if x.dim() == 0:
                x = x.unsqueeze(0)
            v = x.reshape(-1)
            if v.numel() < 2 * self.dim:
                pad = torch.zeros(2 * self.dim - v.numel(), dtype=v.dtype, device=v.device)
                v = torch.cat([v, pad], dim=0)
            elif v.numel() > 2 * self.dim:
                v = v[:2 * self.dim]
            a = v[:self.dim]
            b = v[self.dim:2 * self.dim]
            # cosine similarity
            na = torch.norm(a) + 1e-12
            nb = torch.norm(b) + 1e-12
            sim = torch.dot(a, b) / (na * nb)
            return sim

    # export cosine similarity model
    cs = CosineSimilarityModel(dim=16)
    export_model(cs, 'cosine_similarity', torch.randn(1, 32))

    # ---- small LSTM micro-model ----
    class LSTMSmall(nn.Module):
        def __init__(self, dim=16, hidden=32, num_layers=1):
            super().__init__()
            self.dim = dim
            self.lstm = nn.LSTM(input_size=dim, hidden_size=hidden, num_layers=num_layers)
            self.fc = nn.Linear(hidden, dim)

        def forward(self, x):
            # x: (N, dim) where N is sequence length
            if x.dim() == 1:
                # treat as single-step sequence with dim elements -> reshape to (1, 1, dim)
                seq = x.unsqueeze(1)
            elif x.dim() == 2:
                # (N, dim) -> LSTM expects (seq_len, batch, input_size), set batch=1
                seq = x.unsqueeze(1)
            else:
                seq = x
            out, (h_n, c_n) = self.lstm(seq)
            # return last hidden state projected
            last = h_n[-1]
            return self.fc(last)

    lstm_small = LSTMSmall(dim=16, hidden=32)
    export_model(lstm_small, 'lstm_small', torch.randn(4, 1, 16))


if __name__ == '__main__':
    build_and_export()
