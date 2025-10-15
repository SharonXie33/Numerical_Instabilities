#!/usr/bin/env python3
import os
import numpy as np
from pathlib import Path

out_dir = Path(__file__).resolve().parents[1] / 'results' / 'reproducers' / 'targeted' / 'lstm'
out_dir.mkdir(parents=True, exist_ok=True)

seq_lens = [128, 256]
dim = 16

for seq in seq_lens:
    # zeros
    a = np.zeros((seq, dim), dtype=np.float32)
    np.save(out_dir / f'inputs__lstm_seq{seq}__zeros.npy', a)

    # large values
    a = np.ones((seq, dim), dtype=np.float32) * 1e10
    np.save(out_dir / f'inputs__lstm_seq{seq}__large.npy', a)

    # small/subnormal
    a = np.ones((seq, dim), dtype=np.float32) * 1e-38
    np.save(out_dir / f'inputs__lstm_seq{seq}__subnormal.npy', a)

    # random normal
    a = np.random.randn(seq, dim).astype(np.float32)
    np.save(out_dir / f'inputs__lstm_seq{seq}__rand.npy', a)

    # with NaN in the middle
    a = np.random.randn(seq, dim).astype(np.float32)
    a[seq//2, dim//2] = np.nan
    np.save(out_dir / f'inputs__lstm_seq{seq}__nan.npy', a)

    # with Inf
    a = np.random.randn(seq, dim).astype(np.float32)
    a[seq//3, dim//3] = np.inf
    np.save(out_dir / f'inputs__lstm_seq{seq}__inf.npy', a)

print('Wrote LSTM inputs to', out_dir)
