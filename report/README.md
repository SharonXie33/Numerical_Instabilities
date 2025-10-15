
# Report

This folder contains aggregated reports and visualizations generated from multiple runs. The key charts are embedded below so you can preview them directly in VS Code or on GitHub.

Files in this folder:

- `aggregated_runs.csv` — per-run / per-model / per-framework rows
- `framework_diff.csv` — per-run model/dataset pivot of framework stats
- `summary.md` — human-readable summary
- `instability_by_op_bar.png` — stacked bar chart of NaN / Inf / Errors per model
- `framework_diff_heatmap.png` — heatmap of NaN counts per model vs framework
- `framework_counts_bar.png` — counts of entries per framework
- `model_nan_percent.png` — percent of NaN observations per model

Visualizations

Instability by model (NaN / Inf / Errors):

![Instability by model](instability_by_op_bar.png)

Framework vs Model NaN counts (heatmap):

![Framework vs Model heatmap](framework_diff_heatmap.png)

Number of run entries per framework:

![Framework counts](framework_counts_bar.png)

Percentage of NaN observations per model:

![Model NaN %](model_nan_percent.png)

Regenerate the visualizations from the aggregated CSVs with:

```bash
python ../tools/visualize_results.py --report-dir . --out-dir .
```

Note: images render in VS Code and on GitHub once files are committed.

