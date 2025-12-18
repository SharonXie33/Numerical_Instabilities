# Numerical Instabilities Experiment Overview

This repository hosts the full workflow we used to study floating-point instabilities: composite model generation, KLEE-derived inputs, multi-framework execution, aggregation, visualization, and a browser-ready dashboard. The instructions below explain how to reproduce the entire pipeline from scratch and how to serve the dashboard for demos.

> **Environment assumption**: create and activate a virtual environment in the repo root. For example:
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate
> ```
> Every command that follows is executed from `Numerical_instabilities/`.

## ⚡ One-command pipeline (recommended)

```bash
bash run_pipeline.sh
# or pin the interpreter
# PYTHON_BIN=.venv/bin/python bash run_pipeline.sh
```

The script installs dependencies, rebuilds composite models, runs all evaluators, aggregates results, exports PNGs, and regenerates `report/dashboard/dashboard_data.json`. When it finishes, launch a static server (`python -m http.server 8000`) and open `http://localhost:8000/report/dashboard/` to see the latest visuals.

## Step-by-step pipeline (manual control)

Use these steps when you want to re-run a specific stage. Otherwise, the one-command pipeline already performs 2–9 in order.

1. **Install Python dependencies**
	```bash
	python -m pip install -r tools/requirements.txt
	```
2. **Build and export composed models**
	```bash
	python tools/build_and_export_composed_models.py \
	  --out models/auto_generated \
	  --min-count 10 \
	  --combo-len 3
	```
	Outputs TorchScript/ONNX variants plus `models_meta.json`.
3. **Run the ONNX evaluator (single-framework stats)**
	```bash
	python tools/run_onnx_evaluator.py \
	  --models models/auto_generated/models_meta.json \
	  --inputs parsed_klee_inj_all \
	  --out results/models_eval
	```
	Produces one JSON per model × dataset.
4. **Summarize evaluator outputs**
	```bash
	python tools/compute_summary_stats.py \
	  --dir results/models_eval \
	  --out results/models_summary
	```
	Generates `models_summary.csv` and `.md`.
5. **Execute multi-framework runs**
	```bash
	python runners/run_multi_framework.py \
	  --models models/auto_generated/models_meta.json \
	  --inputs "parsed_klee_inj_all/*/inputs.csv" \
	  --frameworks pytorch,onnx \
	  --out results/runs/run_latest
	```
	Produces `summary.json`/`.csv` under `results/runs/run_latest/`.
6. **Aggregate every run into the report folder**
	```bash
	python runners/compare_summaries.py \
	  --root results/runs \
	  --out report
	```
	Writes `aggregated_runs.csv`, `framework_diff.csv`, and `summary.md`.
7. **Export PNG charts (optional but recommended)**
	```bash
	python tools/visualize_results.py --report-dir report --out-dir report
	```
8. **Generate dashboard data + static assets**
	```bash
	python tools/generate_dashboard.py \
	  --report-dir report \
	  --model-summary results/models_summary/models_summary.csv \
	  --out report/dashboard
	```
	Refreshes `dashboard_data.json` and ensures `index.html`, `styles.css`, and `app.js` are up to date.
9. **Serve the dashboard locally**
	```bash
	python -m http.server 8000
	```
	Visit `http://localhost:8000/report/dashboard/` to explore summary cards, stacked bars (NaN/Inf/Error), dataset stats, top-NaN lists, and the searchable detail table.

##  Demo tips

- If the page says “Failed to load dashboard_data.json”, it usually means step 8 has not been run after the last pipeline execution; regenerate and refresh.
- For classroom demos, pre-run the pipeline so the PNGs and dashboard load instantly, then keep the static server running in another terminal.
- Run `PYTHON_BIN=.venv/bin/python bash run_pipeline.sh` when presenting on a lab machine with multiple Python versions to avoid surprises.

##  Troubleshooting

1. **TorchScript export warnings** – Legacy exporters print warnings; ignore them or switch to `torch.export(..., dynamo=True)` if needed.
2. **UTC deprecation warning** – `generate_dashboard.py` calls `datetime.utcnow()`. The warning is harmless and will be addressed in a future patch.
3. **Port already in use** – Change the server port: `python -m http.server 8080`.

