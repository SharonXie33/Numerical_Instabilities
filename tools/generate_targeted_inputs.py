#!/usr/bin/env python3
"""Generate targeted inputs for numeric-instability testing.
Saves .npy files under results/reproducers/targeted/<category>/
"""
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parents[1]
OUT_BASE = BASE / 'results' / 'reproducers' / 'targeted'
OUT_BASE.mkdir(parents=True, exist_ok=True)

dim = 16

def write(category, name, arr):
    d = OUT_BASE / category
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    np.save(p, np.array(arr, dtype=np.float32))
    print('Wrote', p)

# 1) denom_near_zero: create vectors of length 2*dim (a|b) where b is near-zero
cats = 'denom_near_zero'
vals = [0.0, 1e-16, 1e-12, -1e-12, 1e-8]
for i,v in enumerate(vals):
    a = np.ones(dim, dtype=np.float32) * 1.0
    b = np.ones(dim, dtype=np.float32) * v
    write(cats, f'inputs__{cats}__{i}.npy', np.concatenate([a,b]))

# 2) extreme_magnitudes: single vector of length dim with extreme magnitudes
cats = 'extreme_magnitudes'
exts = [1e6, 1e10, 1e20, -1e10, 1e-30, 1e-45]
for i,e in enumerate(exts):
    write(cats, f'inputs__{cats}__{i}.npy', np.ones(dim) * e)

# 3) pow_edge_cases: construct 2*dim vectors representing pair (a,b)
cats = 'pow_edge_cases'
cases = [ (0.0, -1.0), (-1.0, 0.5), (0.0, 0.5), (2.0, 0.5) ]
for i,(x,y) in enumerate(cases):
    a = np.ones(dim) * x
    b = np.ones(dim) * y
    write(cats, f'inputs__{cats}__{i}.npy', np.concatenate([a,b]))

# 4) sigmoid_extremes
cats = 'sigmoid_extremes'
vals = [1e10, -1e10, 1e6, -1e6]
for i,v in enumerate(vals):
    write(cats, f'inputs__{cats}__{i}.npy', np.ones(dim) * v)

# 5) constant_matrices for CNN: flattened (C,H,W) into 1D so cnn runner can reshape
cats = 'constant_matrices'
shapes = [ (3,16,16), (1,8,8) ]
for i,sh in enumerate(shapes):
    C,H,W = sh
    for val in [0.0, 1.0, 1e-6]:
        arr = np.ones((C,H,W), dtype=np.float32) * val
        write(cats, f'inputs__{cats}__{i}_{int(val)}.npy', arr.ravel())

# 6) cosine_pairs: concatenated a|b with near-parallel, opposite, zero
cats = 'cosine_pairs'
# near-parallel: b = a * (1 + eps)
a = np.linspace(0.1, 1.0, dim)
for i,eps in enumerate([0.0, 1e-6, -1e-6, -1.0]):
    if eps == -1.0:
        b = -a
    else:
        b = a * (1.0 + eps)
    write(cats, f'inputs__{cats}__{i}.npy', np.concatenate([a,b]))
# zero vector case
write('cosine_pairs', 'inputs__cosine_pairs__zero.npy', np.concatenate([np.zeros(dim), np.zeros(dim)]))

# 7) long_sequences: for LSTM/attention: generate seq_len x dim arrays
cats = 'long_sequences'
for seq in [128, 256, 512]:
    # zeros, large, rand, nan
    write(cats, f'inputs__{cats}__{seq}__zeros.npy', np.zeros((seq, dim)))
    write(cats, f'inputs__{cats}__{seq}__large.npy', np.ones((seq, dim)) * 1e6)
    write(cats, f'inputs__{cats}__{seq}__rand.npy', np.random.randn(seq, dim))
    a = np.random.randn(seq, dim).astype(np.float32)
    a[seq//2, dim//2] = np.nan
    write(cats, f'inputs__{cats}__{seq}__nan.npy', a)

print('Generated targeted inputs under', OUT_BASE)
