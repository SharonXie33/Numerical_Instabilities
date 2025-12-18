"""Reference implementations using NumPy. Stable, predictable behavior."""
import numpy as np


def run_task(task, inp: np.ndarray, dtype='float32', compile=False):
    # All reference outputs are numpy arrays
    x = inp.astype(np.float64)
    if task == 'div':
        # for div, expect two inputs: a / b elementwise
        if x.size < 2:
            # broadcast single value
            return np.array([np.nan], dtype=np.float64)
        a = x[0::2]
        b = x[1::2]
        out = a / b
        return out
    elif task == 'log':
        return np.log(x)
    elif task == 'exp':
        return np.exp(x)
    elif task == 'pow':
        # treat pairs
        if x.size < 2:
            return np.array([np.nan], dtype=np.float64)
        a = x[0::2]
        b = x[1::2]
        return np.power(a, b)
    elif task == 'sigmoid':
        y = 1.0 / (1.0 + np.exp(-x))
        return y
    elif task == 'softmax':
        # treat entire vector
        m = np.max(x)
        ex = np.exp(x - m)
        return ex / np.sum(ex)
    elif task == 'sub':
        if x.size < 2:
            return np.array([np.nan], dtype=np.float64)
        a = x[0::2]
        b = x[1::2]
        return a - b
    elif task == 'cossim':
        # cosine similarity between first half and second half
        n = x.size // 2
        if n == 0:
            return np.array([np.nan], dtype=np.float64)
        a = x[:n]
        b = x[n:2*n]
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return np.array([np.nan], dtype=np.float64)
        return np.array([np.dot(a,b)/denom], dtype=np.float64)
    elif task == 'mlp':
        # tiny deterministic MLP reference
        W1 = np.ones((max(1, x.size), max(1, x.size))) * 0.01
        h = np.tanh(x @ W1)
        return h
    else:
        raise NotImplementedError(task)
