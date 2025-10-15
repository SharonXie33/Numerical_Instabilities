Runtime runners and install notes
================================

This project includes runner stubs for TVM and TensorRT:

- `tools/run_tvm_on_repro.py` — attempts to compile an ONNX model with TVM (relay) and run it on CPU. Requires TVM installed with Python bindings.
- `tools/run_tensorrt_on_repro.py` — a stub that will guide you to use `trtexec` or install TensorRT Python bindings. Building a robust TRT runner requires CUDA & TensorRT and careful engine building.

Installing TVM (short):

1. Follow the official guide: https://tvm.apache.org/docs/install/index.html
2. Minimal build steps (Linux/macOS variations exist):

```bash
# clone tvm
git clone --recursive https://github.com/apache/tvm tvm
cd tvm
# edit cmake/config.cmake or use the python build instructions to configure
mkdir build; cd build
cmake .. -DCMAKE_BUILD_TYPE=Release \
  -DUSE_LLVM=ON \
  -DUSE_CUDA=OFF
make -j8
cd ../python
python -m pip install -e .
```

Installing TensorRT (short):

1. TensorRT is distributed by NVIDIA and typically installed via package manager or tarball. It requires a matching CUDA & driver stack.
2. For model conversion/use, `trtexec` (provided in the TensorRT package) can convert ONNX to TRT engine:

```bash
# convert
trtexec --onnx=model.onnx --saveEngine=model.trt
# run with input (trtexec has options to provide inputs) or use onnx-tensorrt
```

Notes:
- TensorRT Python bindings (`tensorrt`) and PyCUDA are optional but allow in-process engine build/execution. They must match system CUDA/driver.
- TVM builds are heavier; consider using Docker images if you don't want to build locally.

If you want, I can attempt to add a more complete TensorRT runner, but I will need access to a machine/container with CUDA and TensorRT installed.
