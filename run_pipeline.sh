#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN=${PYTHON_BIN:-python}
PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$PROJECT_ROOT"

info() {
  printf '\n[run_pipeline] %s\n' "$1"
}

REQ_FILE="tools/requirements.txt"
if [[ -f "$REQ_FILE" ]]; then
  info "Installing/updating Python dependencies"
  "$PYTHON_BIN" -m pip install -r "$REQ_FILE"
fi

info "Generating composed models"
"$PYTHON_BIN" tools/build_and_export_composed_models.py \
  --out models/auto_generated \
  --min-count 10 \
  --combo-len 3

info "Running ONNX evaluator"
"$PYTHON_BIN" tools/run_onnx_evaluator.py \
  --models models/auto_generated/models_meta.json \
  --inputs parsed_klee_inj_all \
  --out results/models_eval

info "Aggregating evaluator statistics"
"$PYTHON_BIN" tools/compute_summary_stats.py \
  --dir results/models_eval \
  --out results/models_summary

info "Running multi-framework evaluation"
"$PYTHON_BIN" runners/run_multi_framework.py \
  --models models/auto_generated/models_meta.json \
  --inputs "parsed_klee_inj_all/*/inputs.csv" \
  --frameworks pytorch,onnx \
  --out results/runs/run_latest

info "Comparing runs"
"$PYTHON_BIN" runners/compare_summaries.py \
  --root results/runs \
  --out report

info "Rendering PNG charts"
"$PYTHON_BIN" tools/visualize_results.py \
  --report-dir report \
  --out-dir report

info "Generating dashboard data"
"$PYTHON_BIN" tools/generate_dashboard.py \
  --report-dir report \
  --model-summary results/models_summary/models_summary.csv \
  --out report/dashboard

info "Pipeline complete! Serve report/dashboard/ via 'python -m http.server' if needed."
