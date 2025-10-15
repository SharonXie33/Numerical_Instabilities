"""Metrics for comparing numeric outputs.
Provides max relative error, ULP distance (approx via spint), NaN/Inf counts.
"""
import numpy as np
import math


def dtype_name(dtype):
    return str(dtype)


def count_nan_inf(a):
    a = np.asarray(a)
    return int(np.isnan(a).sum()), int(np.isinf(a).sum())


def max_rel_error(a, b, eps=1e-12):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    valid = ~np.logical_or(np.isnan(a), np.isnan(b))
    if not np.any(valid):
        return float('nan')
    denom = np.maximum(np.abs(b[valid]), eps)
    rel = np.abs(a[valid] - b[valid]) / denom
    return float(np.nanmax(rel))


def float_to_int_bits(f):
    # works for float64
    return np.frombuffer(np.asarray(f, dtype=np.float64).tobytes(), dtype=np.int64)


def ulp_distance(a, b):
    # approximate ULP distance by interpreting bits as int64
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    # handle NaN/Inf by masking
    mask = np.logical_and(np.isfinite(a), np.isfinite(b))
    if not np.any(mask):
        return float('nan')
    ai = np.frombuffer(a[mask].tobytes(), dtype=np.int64)
    bi = np.frombuffer(b[mask].tobytes(), dtype=np.int64)
    return float(np.max(np.abs(ai - bi)))


def compute_metrics_for_pair(out_unstable, out_ref):
    nan_un, inf_un = count_nan_inf(out_unstable)
    nan_ref, inf_ref = count_nan_inf(out_ref)
    max_rel = max_rel_error(out_unstable, out_ref)
    max_ulp = ulp_distance(out_unstable, out_ref)
    return {
        'max_rel_error': max_rel,
        'max_ulp': max_ulp,
        'nan_unstable': nan_un,
        'nan_ref': nan_ref,
        'inf_unstable': inf_un,
        'inf_ref': inf_ref,
    }
