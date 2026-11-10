
from pathlib import Path

import pandas as pd

from src.history.history_tracker import (
    DEFAULT_HISTORY_PATH,
    HISTORY_FIELDS,
)


# Metrics where higher values indicate better data quality.
HIGHER_IS_BETTER = [
    "quality_score",
    "completeness",
]

# Metrics where lower values indicate better data quality.
LOWER_IS_BETTER = [
    "missing_values",
    "duplicate_rows",
    "validation_issues",
    "anomalies",
]


def compare_quality_history(history_path=None):
    """
    Compare the latest two successful pipeline executions.

    Returns:
        Dictionary containing previous execution, latest execution,
        metric differences, and improvement statuses.
    """

    file_path = (
        Path(history_path)
        if history_path
        else DEFAULT_HISTORY_PATH
    )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Quality history file not found: {file_path}"
        )

    history_df = pd.read_csv(file_path)

    if history_df.empty:
        raise ValueError("Quality history contains no records.")

    missing_columns = [
        column
        for column in HISTORY_FIELDS
        if column not in history_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"History file is missing columns: {missing_columns}"
        )

    if len(history_df) < 2:
        raise ValueError(
            "At least two executions are required for comparison."
        )

    history_df["parsed_timestamp"] = pd.to_datetime(
        history_df["timestamp"],
        errors="coerce",
        utc=True,
    )

    history_df = history_df.dropna(
        subset=["parsed_timestamp"]
    ).sort_values("parsed_timestamp")

    if len(history_df) < 2:
        raise ValueError(
            "At least two valid execution records are required."
        )

    previous = history_df.iloc[-2]
    latest = history_df.iloc[-1]

    comparison = {}

    for metric in HIGHER_IS_BETTER + LOWER_IS_BETTER:

        previous_value = pd.to_numeric(
            previous[metric],
            errors="coerce",
        )

        latest_value = pd.to_numeric(
            latest[metric],
            errors="coerce",
        )

        if pd.isna(previous_value) or pd.isna(latest_value):
            raise ValueError(
                f"Invalid numeric values found for metric: {metric}"
            )

        difference = round(
            float(latest_value - previous_value),
            2,
        )

        if difference == 0:
            status = "unchanged"

        elif metric in HIGHER_IS_BETTER:
            status = (
                "improved"
                if difference > 0
                else "regressed"
            )

        else:
            status = (
                "improved"
                if difference < 0
                else "regressed"
            )

        comparison[metric] = {
            "previous": float(previous_value),
            "latest": float(latest_value),
            "difference": difference,
            "status": status,
        }

    return {
        "previous_execution": previous.to_dict(),
        "latest_execution": latest.to_dict(),
        "comparison": comparison,
    }
