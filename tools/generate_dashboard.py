#!/usr/bin/env python3
"""Generate dashboard data and static assets for the visualization site.

This script converts the existing CSV/JSON summaries into a single
`dashboard_data.json` blob that can be consumed by the front-end located under
`report/dashboard/`.

Example:
    python tools/generate_dashboard.py \
        --report-dir report \
        --model-summary results/models_summary/models_summary.csv \
        --out report/dashboard
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, Iterable, List, Optional


def _safe_int(value: Optional[str]) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _load_csv(path: str, *, int_fields: Iterable[str] = ()) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in int_fields:
                row[field] = _safe_int(row.get(field))
            rows.append(row)
    return rows


def build_model_stats(entries: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    agg: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "num_nan": 0, "num_inf": 0, "num_error": 0})
    for entry in entries:
        model = str(entry.get("model", "UNKNOWN"))
        agg[model]["total"] += int(entry.get("total", 0))
        agg[model]["num_nan"] += int(entry.get("num_nan", 0))
        agg[model]["num_inf"] += int(entry.get("num_inf", 0))
        agg[model]["num_error"] += int(entry.get("num_error", 0))
    result = []
    for model, stats in agg.items():
        total = stats["total"] or 1
        nan_rate = stats["num_nan"] / total
        inf_rate = stats["num_inf"] / total
        err_rate = stats["num_error"] / total
        result.append(
            {
                "model": model,
                "total": stats["total"],
                "num_nan": stats["num_nan"],
                "num_inf": stats["num_inf"],
                "num_error": stats["num_error"],
                "nan_rate": nan_rate,
                "inf_rate": inf_rate,
                "error_rate": err_rate,
            }
        )
    result.sort(key=lambda r: (r["num_nan"], r["num_inf"], r["num_error"]), reverse=True)
    return result


def build_framework_stats(entries: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    agg: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "num_nan": 0, "num_inf": 0, "num_error": 0})
    for entry in entries:
        fw = str(entry.get("framework", "UNKNOWN"))
        agg[fw]["total"] += int(entry.get("total", 0))
        agg[fw]["num_nan"] += int(entry.get("num_nan", 0))
        agg[fw]["num_inf"] += int(entry.get("num_inf", 0))
        agg[fw]["num_error"] += int(entry.get("num_error", 0))
    result = []
    for fw, stats in agg.items():
        total = stats["total"] or 1
        result.append(
            {
                "framework": fw,
                "total": stats["total"],
                "num_nan": stats["num_nan"],
                "num_inf": stats["num_inf"],
                "num_error": stats["num_error"],
                "nan_rate": stats["num_nan"] / total,
                "inf_rate": stats["num_inf"] / total,
                "error_rate": stats["num_error"] / total,
            }
        )
    result.sort(key=lambda r: r["framework"])
    return result


def build_dataset_stats(entries: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    agg: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "num_nan": 0, "num_inf": 0, "num_error": 0})
    for entry in entries:
        ds = str(entry.get("dataset", "UNKNOWN"))
        agg[ds]["total"] += int(entry.get("total", 0))
        agg[ds]["num_nan"] += int(entry.get("num_nan", 0))
        agg[ds]["num_inf"] += int(entry.get("num_inf", 0))
        agg[ds]["num_error"] += int(entry.get("num_error", 0))
    result = []
    for ds, stats in agg.items():
        total = stats["total"] or 1
        result.append(
            {
                "dataset": ds,
                "total": stats["total"],
                "num_nan": stats["num_nan"],
                "num_inf": stats["num_inf"],
                "num_error": stats["num_error"],
                "nan_rate": stats["num_nan"] / total,
                "inf_rate": stats["num_inf"] / total,
                "error_rate": stats["num_error"] / total,
            }
        )
    result.sort(key=lambda r: r["dataset"])
    return result


def load_framework_diff(path: str) -> List[Dict[str, object]]:
    if not os.path.exists(path):
        return []
    rows = _load_csv(path, int_fields=("max_nan", "max_inf", "max_error"))
    for row in rows:
        stats = row.get("stats_json")
        if isinstance(stats, str):
            try:
                row["stats_json"] = json.loads(stats)
            except json.JSONDecodeError:
                pass
    return rows


def load_model_summary(path: Optional[str]) -> List[Dict[str, object]]:
    if not path or not os.path.exists(path):
        return []
    return _load_csv(path, int_fields=("tests", "has_nan", "has_inf"))


def summarize(entries: List[Dict[str, object]]) -> Dict[str, object]:
    total_entries = len(entries)
    total_nan = sum(int(e.get("num_nan", 0)) for e in entries)
    total_inf = sum(int(e.get("num_inf", 0)) for e in entries)
    total_err = sum(int(e.get("num_error", 0)) for e in entries)
    runs = sorted({str(e.get("run", "")) for e in entries})
    models = sorted({str(e.get("model", "")) for e in entries})
    datasets = sorted({str(e.get("dataset", "")) for e in entries})
    frameworks = sorted({str(e.get("framework", "")) for e in entries})

    run_counter = Counter(str(e.get("run", "")) for e in entries)
    run_summary = [
        {"run": run, "entries": count}
        for run, count in sorted(run_counter.items(), key=lambda item: item[1], reverse=True)
    ]

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_entries": total_entries,
        "total_nan": total_nan,
        "total_inf": total_inf,
        "total_error": total_err,
        "num_runs": len(runs),
        "num_models": len(models),
        "num_datasets": len(datasets),
        "num_frameworks": len(frameworks),
        "runs": run_summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate dashboard data JSON")
    parser.add_argument("--report-dir", default="report", help="Directory containing aggregated CSVs")
    parser.add_argument(
        "--model-summary",
        default="results/models_summary/models_summary.csv",
        help="CSV file produced by tools/compute_summary_stats.py",
    )
    parser.add_argument("--out", default="report/dashboard", help="Output directory for dashboard assets")
    args = parser.parse_args()

    agg_csv = os.path.join(args.report_dir, "aggregated_runs.csv")
    if not os.path.exists(agg_csv):
        raise SystemExit(f"Aggregated CSV not found: {agg_csv}")

    entries = _load_csv(agg_csv, int_fields=("total", "num_nan", "num_inf", "num_error"))
    summary = summarize(entries)
    model_stats = build_model_stats(entries)
    framework_stats = build_framework_stats(entries)
    dataset_stats = build_dataset_stats(entries)

    diff_csv = os.path.join(args.report_dir, "framework_diff.csv")
    framework_diff = load_framework_diff(diff_csv)
    model_summary = load_model_summary(args.model_summary)

    data = {
        "summary": summary,
        "entries": entries,
        "model_stats": model_stats,
        "framework_stats": framework_stats,
        "dataset_stats": dataset_stats,
        "framework_diff": framework_diff,
        "model_summary": model_summary,
    }

    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, "dashboard_data.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
