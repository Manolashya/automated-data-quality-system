
import csv
from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_HISTORY_PATH = (
    PROJECT_ROOT / "reports" / "quality_history.csv"
)

HISTORY_FIELDS = [
    "timestamp",
    "dataset_name",
    "rows",
    "columns",
    "quality_score",
    "completeness",
    "missing_values",
    "duplicate_rows",
    "validation_issues",
    "anomalies",
]


def save_quality_history(
    profiling_report,
    validation_issues,
    anomaly_results,
    history_path=None
):
    """Save one pipeline execution to the quality history CSV."""

    if not isinstance(profiling_report, dict):
        raise TypeError("profiling_report must be a dictionary.")

    if not isinstance(validation_issues, list):
        raise TypeError("validation_issues must be a list.")

    if not isinstance(anomaly_results, pd.DataFrame):
        raise TypeError("anomaly_results must be a pandas DataFrame.")

    required_fields = [
        "file_name",
        "rows",
        "column_count",
        "completeness_score",
        "missing_values",
        "overall_quality_score",
        "duplicate_rows",
    ]

    for field in required_fields:
        if field not in profiling_report:
            raise ValueError(
                f"Missing required profiling field: {field}"
            )

    completeness_scores = profiling_report["completeness_score"]
    missing_values_by_column = profiling_report["missing_values"]

    if not isinstance(completeness_scores, dict) or not completeness_scores:
        raise ValueError("Completeness scores must be a non-empty dictionary.")

    if not isinstance(missing_values_by_column, dict):
        raise ValueError("Missing values must be a dictionary.")

    if "Anomaly" not in anomaly_results.columns:
        raise ValueError("Anomaly results must contain an 'Anomaly' column.")

    completeness = round(
        sum(completeness_scores.values()) / len(completeness_scores),
        2
    )

    total_missing_values = sum(missing_values_by_column.values())

    anomaly_count = int(
        (anomaly_results["Anomaly"] == "Anomaly").sum()
    )

    record = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "dataset_name": profiling_report["file_name"],
        "rows": profiling_report["rows"],
        "columns": profiling_report["column_count"],
        "quality_score": profiling_report["overall_quality_score"],
        "completeness": completeness,
        "missing_values": total_missing_values,
        "duplicate_rows": profiling_report["duplicate_rows"],
        "validation_issues": len(validation_issues),
        "anomalies": anomaly_count,
    }

    output_path = Path(history_path) if history_path else DEFAULT_HISTORY_PATH

    output_path.parent.mkdir(parents=True, exist_ok=True)

    write_header = (
        not output_path.exists() or output_path.stat().st_size == 0
    )

    with output_path.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=HISTORY_FIELDS
        )

        if write_header:
            writer.writeheader()

        writer.writerow(record)

    return output_path
