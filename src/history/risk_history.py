import csv
import json
from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_RISK_HISTORY_PATH = (
    PROJECT_ROOT / "reports" / "risk_history.csv"
)

RISK_HISTORY_FIELDS = [
    "timestamp",
    "dataset_name",
    "risk_score",
    "risk_level",
    "quality_score",
    "missing_percentage",
    "duplicate_percentage",
    "trend",
    "recurring_issues",
]


def save_risk_history(risk_result, history_path=None):
    """Append one risk assessment to the risk history CSV."""

    if not isinstance(risk_result, dict):
        raise TypeError("risk_result must be a dictionary.")

    required_fields = [
        "dataset_name",
        "risk_score",
        "risk_level",
        "quality_score",
        "missing_percentage",
        "duplicate_percentage",
        "trend",
        "recurring_issues",
    ]

    missing_fields = [
        field for field in required_fields
        if field not in risk_result
    ]

    if missing_fields:
        raise ValueError(
            f"Missing required risk fields: {missing_fields}"
        )

    if not str(risk_result["dataset_name"]).strip():
        raise ValueError("dataset_name cannot be empty.")

    numeric_fields = [
        "risk_score",
        "quality_score",
        "missing_percentage",
        "duplicate_percentage",
    ]

    record = {}

    for field in numeric_fields:
        try:
            value = float(risk_result[field])
        except (TypeError, ValueError):
            raise ValueError(f"{field} must be numeric.")

        if not 0 <= value <= 100:
            raise ValueError(f"{field} must be between 0 and 100.")

        record[field] = round(value, 2)

    if not isinstance(risk_result["recurring_issues"], list):
        raise TypeError("recurring_issues must be a list.")

    record.update({
        "timestamp": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "dataset_name": str(risk_result["dataset_name"]),
        "risk_level": str(risk_result["risk_level"]),
        "trend": str(risk_result["trend"]),
        "recurring_issues": json.dumps(
            risk_result["recurring_issues"]
        ),
    })

    output_path = (
        Path(history_path)
        if history_path is not None
        else DEFAULT_RISK_HISTORY_PATH
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    write_header = (
        not output_path.exists()
        or output_path.stat().st_size == 0
    )

    with output_path.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=RISK_HISTORY_FIELDS
        )

        if write_header:
            writer.writeheader()

        writer.writerow(record)

    return output_path


def load_risk_history(history_path=None):
    """Load saved risk assessments as a pandas DataFrame."""

    input_path = (
        Path(history_path)
        if history_path is not None
        else DEFAULT_RISK_HISTORY_PATH
    )

    if not input_path.exists():
        return pd.DataFrame(columns=RISK_HISTORY_FIELDS)

    return pd.read_csv(input_path)
