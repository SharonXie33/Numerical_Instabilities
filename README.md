# Numerical Instabilities for AI Compilers — FPGen + KLEE

Overview
--
This repository provides an automated pipeline to discover and compare numerical instabilities (NaN / Inf / overflow / underflow / other runtime errors) across operator compositions and multiple AI runtimes. The goal is reproducible experiments and clear, shareable summaries.

Main features
--
- Symbolic-input generation using FPGen/KLEE (container scripts included)
- Automated generation of operator-composition models (PyTorch -> TorchScript + ONNX)
- Multi-backend evaluation (PyTorch, ONNX Runtime; optional TVM / TensorRT)
- Aggregation of per-run summaries and visualization generation (CSV, Markdown, PNG)

Repository layout
--
- `tools/` — model generation, ONNX evaluation and summary tools
- `runners/` — multi-framework runners and comparison utilities
- `models/` — exported example models (TorchScript + ONNX)
- `parsed_klee_inj_all/` — parsed FPGen/KLEE input CSVs (sample or real)
- `results/` — per-run outputs and summaries
- `report/` — aggregated CSVs, Markdown summary and PNG visualizations

Requirements
--
- Python 3.8+ (recommended: use a virtual environment)
- PyTorch, ONNX, ONNX Runtime, NumPy, Matplotlib
- For TVM / TensorRT evaluation: platform-specific installs (Linux + NVIDIA/CUDA for TensorRT)

Quick start (minimal reproducible example)
--
From the repository root, using your virtual environment or system python:

```bash
python -m pip install -r tools/requirements.txt
python tools/build_and_export_composed_models.py --out models/auto_generated --min-count 10 --combo-len 3
python tools/run_onnx_evaluator.py --models models/auto_generated/models_meta.json --inputs parsed_klee_inj_all --out results/models_eval
python tools/compute_summary_stats.py --dir results/models_eval --out results/models_summary
python runners/compare_summaries.py --root results/runs --out report
python tools/visualize_results.py --report-dir report --out-dir report
```

Reproducing larger FPGen runs
--
- FPGen/KLEE long runs are expected to run inside the provided container scripts (see `run_symbolics.sh` and `generate_inputs.sh`).
- Use the container helpers to compile/link bitcode and run KLEE; then use the provided parsers to convert `.ktest` outputs into CSVs under `parsed_klee_inj_all/`.

Key visualizations
--
The `report/` directory contains PNGs and CSVs summarizing aggregated results. Key images (already generated in this repo):

- `report/instability_by_op_bar.png` — per-model counts of NaN/Inf/errors
- `report/framework_diff_heatmap.png` — heatmap comparing frameworks vs. models
- `report/framework_counts_bar.png` — per-framework aggregate counts
- `report/model_nan_percent.png` — normalized NaN percentage per model

How to run custom experiments
--
1. Place or generate parsed FPGen/KLEE inputs under `parsed_klee_inj_all/` (CSV files).
2. Ensure `models/` contains the models you want to evaluate and that `models_meta.json` lists them.
3. Run the multi-framework runner:

```bash
python runners/run_multi_framework.py --models models/auto_generated/models_meta.json --inputs "parsed_klee_inj_all/*/inputs.csv" --frameworks pytorch,onnx --out results/summary_multi
```

4. Aggregate multiple runs and generate the report:

```bash
python runners/compare_summaries.py --root results/runs --out report
python tools/visualize_results.py --report-dir report --out-dir report
```

Notes & limitations
--
- TVM and TensorRT support require platform-specific installations and are optional; the scripts will skip unavailable backends.
- Large model artifacts, raw KLEE outputs and large result directories should be excluded from the published repository (use `.gitignore`).

Contributing
--
- Contributions are welcome via pull requests. When adding models or large reproducer data, include a short descriptor and keep large files out of git.

Support / Issues
--
- For reproducibility questions, open an issue with a minimal reproducer (model + inputs) and environment details (OS, Python, GPU).

License
--
- Add a `LICENSE` file at the repository root to indicate the intended license (e.g., MIT, Apache 2.0).
