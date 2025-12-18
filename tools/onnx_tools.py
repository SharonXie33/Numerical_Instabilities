"""Tiny ONNX export helpers. Export torch modules if available."""
try:
    import torch
    TORCH = True
except Exception:
    TORCH = False


def export_torch_callable(callable_fn, sample_input, out_path):
    if not TORCH:
        raise RuntimeError('torch not available for ONNX export')
    # Expect callable_fn to be a torch.nn.Module or a callable that accepts torch.Tensor
    import torch
    mod = callable_fn
    if not isinstance(mod, torch.nn.Module):
        # wrap
        class Wrap(torch.nn.Module):
            def __init__(self, f):
                super().__init__()
                self.f = f
            def forward(self, x):
                return self.f(x)
        mod = Wrap(callable_fn)

    mod.eval()
    with torch.no_grad():
        torch.onnx.export(mod, sample_input, out_path, opset_version=13)
    return out_path
