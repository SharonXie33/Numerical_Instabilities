Tools to generate models, export to ONNX, run ONNX Runtime evaluations and aggregate summaries.

Quick flow:
- `generate_and_export_models.py` -> produces `models/models_meta.json`, TorchScript and ONNX files
- `run_onnx_evaluator.py` -> runs ONNX models on parsed inputs (from `parsed_klee_inj_all`) and writes results to `results/models_eval`
- `compute_summary_stats.py` -> aggregates `results/models_eval/*.json` into CSV/MD summary

Example:
```
python3 tools/generate_and_export_models.py --out models --max-len 2
python3 -m pip install -r tools/requirements.txt --user
python3 tools/run_onnx_evaluator.py --models models/models_meta.json --inputs parsed_klee_inj_all --out results/models_eval
python3 tools/compute_summary_stats.py --dir results/models_eval --out results/models_summary
```
