#!/usr/bin/env python3
"""Run an ONNX model with TensorRT (Python bindings) on repro inputs and write summary.json / summary.csv.

This script attempts an in-process TensorRT engine build and execution using the Python bindings
(tensorrt + pycuda). If those are not available it prints guidance on using `trtexec` or installing
the bindings.

Notes:
- Building engines with dynamic shapes may require explicit shape setting via the execution context.
- This is a best-effort implementation; adjust workspace size and builder flags for large models.
"""
import argparse
from pathlib import Path
import json
import csv
import numpy as np


def read_repro_input(path: Path):
    if path.suffix == '.npy':
        return np.load(str(path)).astype(np.float32)
    if path.suffix == '.csv':
        try:
            a = np.loadtxt(str(path), delimiter=',')
            if a.ndim == 0:
                a = np.array([a], dtype=np.float32)
            return a.astype(np.float32)
        except Exception:
            txt = path.read_text().strip()
            parts = [p for p in txt.replace('\n', ',').split(',') if p!='']
            vals = []
            for p in parts:
                try:
                    vals.append(float(p))
                except Exception:
                    lp = p.lower()
                    if lp == 'nan':
                        vals.append(np.nan)
                    elif lp in ('inf','+inf'):
                        vals.append(np.inf)
                    elif lp == '-inf':
                        vals.append(-np.inf)
            return np.array(vals, dtype=np.float32)
    txt = path.read_text().strip()
    parts = [p for p in txt.replace('\n', ',').split(',') if p!='']
    vals = []
    for p in parts:
        try:
            vals.append(float(p))
        except Exception:
            lp = p.lower()
            if lp == 'nan':
                vals.append(np.nan)
            elif lp in ('inf','+inf'):
                vals.append(np.inf)
            elif lp == '-inf':
                vals.append(-np.inf)
    return np.array(vals, dtype=np.float32)


def summarize(rows, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    js = {'n': len(rows), 'results': rows}
    with open(outdir / 'summary.json', 'w') as f:
        json.dump(js, f, indent=2)
    with open(outdir / 'summary.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['repro_file','input_len','has_nan_in','has_inf_in','output','has_nan_out','has_inf_out','error'])
        for r in rows:
            inp = r.get('input')
            has_nan_in = bool(np.isnan(inp).any()) if inp is not None else ''
            has_inf_in = bool(np.isinf(inp).any()) if inp is not None else ''
            outv = r.get('output')
            has_nan_out = ''
            has_inf_out = ''
            if outv is not None:
                try:
                    arr = np.array(outv, dtype=float)
                    has_nan_out = bool(np.isnan(arr).any())
                    has_inf_out = bool(np.isinf(arr).any())
                except Exception:
                    pass
            w.writerow([r.get('repro_file'), len(inp) if inp is not None else 0, has_nan_in, has_inf_in, json.dumps(outv), has_nan_out, has_inf_out, r.get('error') or ''])


def build_engine_from_onnx(onnx_path: str, logger, max_workspace_size=1<<30, fp16=False):
    import tensorrt as trt
    builder = trt.Builder(logger)
    network_flags = (1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    network = builder.create_network(network_flags)
    parser = trt.OnnxParser(network, logger)
    with open(onnx_path, 'rb') as f:
        if not parser.parse(f.read()):
            raise RuntimeError('Failed to parse ONNX')
    config = builder.create_builder_config()
    config.max_workspace_size = max_workspace_size
    if fp16 and builder.platform_has_fast_fp16:
        config.set_flag(trt.BuilderFlag.FP16)
    engine = builder.build_engine(network, config)
    if engine is None:
        raise RuntimeError('Failed to build TensorRT engine')
    return engine


def trt_run(onnx_path: str, repro_dir: str, outdir: str):
    try:
        import tensorrt as trt
        import pycuda.driver as cuda
        import pycuda.autoinit
    except Exception as e:
        print('TensorRT python bindings not available:', e)
        print('You can convert ONNX to a TRT engine using trtexec:')
        print('  trtexec --onnx=model.onnx --saveEngine=model.trt')
        print('Then execute the engine or install TensorRT Python bindings.')
        raise SystemExit(1)

    TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
    engine = build_engine_from_onnx(onnx_path, TRT_LOGGER)
    context = engine.create_execution_context()

    repro = Path(repro_dir)
    repro_files = sorted([q for q in repro.iterdir() if q.suffix in ('.npy', '.csv')])
    rows = []

    # prepare bindings
    bindings = [None] * engine.num_bindings
    d_inputs = {}
    for i in range(engine.num_bindings):
        name = engine.get_binding_name(i)
        dtype = trt.nptype(engine.get_binding_dtype(name)) if isinstance(name, str) else trt.nptype(engine.get_binding_dtype(i))

    for rp in repro_files:
        try:
            arr = read_repro_input(rp)
        except Exception as e:
            rows.append({'repro_file': str(rp), 'input': None, 'output': None, 'error': 'read error: '+str(e)})
            continue
        x = arr
        if x.ndim == 1:
            x = x.reshape(1, -1)
        # set binding shape if dynamic
        # find first input binding index
        input_idx = None
        for i in range(engine.num_bindings):
            if engine.binding_is_input(i):
                input_idx = i
                break
        if input_idx is None:
            rows.append({'repro_file': str(rp), 'input': arr.tolist(), 'output': None, 'error': 'no input binding'})
            continue

        # determine desired shape
        bind_shape = list(engine.get_binding_shape(input_idx))
        # replace -1 with actual dims
        # if bind_shape has -1 (dynamic), try to set batch dimension to x.shape[0]
        desired_shape = []
        if any([d == -1 for d in bind_shape]):
            # naive mapping: if len(bind_shape) == x.ndim or bind_shape[1:] matches
            if len(bind_shape) == x.ndim:
                desired_shape = list(x.shape)
            elif len(bind_shape) == x.ndim + 1:
                # batch dim + x.shape
                desired_shape = [x.shape[0]] + list(x.shape[1:])
            else:
                # fallback: set batch to 1 and try to fit
                desired_shape = [1] + list(x.shape[1:]) if x.ndim>1 else [1, x.size]
        else:
            desired_shape = bind_shape

        try:
            context.set_binding_shape(input_idx, tuple(desired_shape))
        except Exception:
            # ignore if cannot set
            pass

        # allocate device buffers
        import pycuda.driver as cuda
        host_inputs = []
        device_inputs = []
        host_outputs = []
        device_outputs = []
        bindings = []
        for i in range(engine.num_bindings):
            shape = context.get_binding_shape(i)
            if shape is None:
                # fallback to engine binding shape
                shape = engine.get_binding_shape(i)
            size = 1
            for d in shape:
                size *= int(d)
            dtype = np.float32
            host_mem = cuda.pagelocked_empty(size, dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)
            bindings.append(int(device_mem))
            if engine.binding_is_input(i):
                host_inputs.append(host_mem)
                device_inputs.append(device_mem)
            else:
                host_outputs.append(host_mem)
                device_outputs.append(device_mem)

        # copy input into host_inputs[0]
        in_host = host_inputs[0]
        flat = x.astype(np.float32).ravel()
        if flat.size > in_host.size:
            # truncate
            in_host[:in_host.size] = flat[:in_host.size]
        else:
            in_host[:flat.size] = flat

        try:
            # copy to device
            cuda.memcpy_htod(device_inputs[0], in_host)
            # run
            context.execute_v2(bindings)
            # copy outputs back
            out_arrs = []
            for idx, dev in enumerate(device_outputs):
                host = host_outputs[idx]
                cuda.memcpy_dtoh(host, dev)
                out_arrs.append(np.array(host).reshape(-1).tolist())
            # return first output
            rows.append({'repro_file': str(rp), 'input': arr.tolist(), 'output': out_arrs[0] if out_arrs else None, 'error': None})
        except Exception as e:
            rows.append({'repro_file': str(rp), 'input': arr.tolist(), 'output': None, 'error': str(e)})

    summarize(rows, Path(outdir))
    print('Wrote', Path(outdir) / 'summary.json')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--onnx', required=True)
    p.add_argument('--repro', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()
    trt_run(args.onnx, args.repro, args.out)


if __name__ == '__main__':
    main()
