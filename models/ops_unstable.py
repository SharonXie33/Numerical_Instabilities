"""Unstable implementations: try to use torch (simulates a different backend)."""
import numpy as np

try:
    import torch
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False


def _to_torch(x, dtype=torch.float32 if TORCH_AVAILABLE else None):
    if not TORCH_AVAILABLE:
        return None
    return torch.tensor(x.astype(np.float32))


def run_task(task, inp: np.ndarray, dtype='float32', compile=False):
    x = inp.astype(np.float32)
    if task == 'div':
        if x.size < 2:
            return np.array([np.nan], dtype=np.float32)
        a = x[0::2]
        b = x[1::2]
        if TORCH_AVAILABLE:
            ta = _to_torch(a)
            tb = _to_torch(b)
            try:
                out = (ta / tb).cpu().numpy()
            except Exception:
                # simulate unstable behavior for extreme values
                out = np.array([np.inf if v==0 else ai/bi for ai,bi,v in zip(a,b,b)], dtype=np.float32)
            return out
        else:
            return a / b
    elif task == 'log':
        if TORCH_AVAILABLE:
            t = _to_torch(x)
            return torch.log(t).cpu().numpy()
        return np.log(x)
    elif task == 'exp':
        if TORCH_AVAILABLE:
            t = _to_torch(x)
            return torch.exp(t).cpu().numpy()
        return np.exp(x)
    elif task == 'pow':
        if x.size < 2:
            return np.array([np.nan], dtype=np.float32)
        a = x[0::2]
        b = x[1::2]
        if TORCH_AVAILABLE:
            ta = _to_torch(a)
            tb = _to_torch(b)
            return torch.pow(ta, tb).cpu().numpy()
        return np.power(a, b)
    elif task == 'sigmoid':
        if TORCH_AVAILABLE:
            t = _to_torch(x)
            return (1.0/(1.0+torch.exp(-t))).cpu().numpy()
        return 1.0/(1.0+np.exp(-x))
    elif task == 'softmax':
        if TORCH_AVAILABLE:
            t = _to_torch(x)
            e = torch.exp(t - torch.max(t))
            return (e / torch.sum(e)).cpu().numpy()
        m = np.max(x)
        ex = np.exp(x - m)
        return ex / np.sum(ex)
    elif task == 'sub':
        if x.size < 2:
            return np.array([np.nan], dtype=np.float32)
        a = x[0::2]
        b = x[1::2]
        if TORCH_AVAILABLE:
            ta = _to_torch(a); tb = _to_torch(b)
            return (ta - tb).cpu().numpy()
        return a - b
    elif task == 'cossim':
        n = x.size // 2
        if n == 0:
            return np.array([np.nan], dtype=np.float32)
        a = x[:n]
        b = x[n:2*n]
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            # simulate PyTorch returning inf in certain cases
            if TORCH_AVAILABLE:
                return np.array([np.inf], dtype=np.float32)
            return np.array([np.nan], dtype=np.float32)
        return np.array([np.dot(a,b)/denom], dtype=np.float32)
    elif task == 'mlp':
        # small pseudo-MLP; if torch available use it (might behave differently)
        if TORCH_AVAILABLE:
            t = _to_torch(x)
            # simple linear transform
            w = torch.ones((t.numel(), t.numel())) * 0.01
            out = torch.tanh(t @ w)
            return out.cpu().numpy()
        W1 = np.ones((max(1, x.size), max(1, x.size))) * 0.01
        h = np.tanh(x @ W1)
        return h
    else:
        raise NotImplementedError(task)
