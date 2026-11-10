
import pandas as pd
import pytest

from src.history.history_comparator import (
    compare_quality_history,
)


@pytest.fixture
def history_file(tmp_path):
    """Create a temporary history CSV with two executions."""

    history_path = tmp_path / "quality_history.csv"

    history_data = [
        {
            "timestamp": "2026-11-10T18:00:00+05:30",
            "dataset_name": "customer_data.csv",
            "rows": 15,
            "columns": 10,
            "quality_score": 95.00,
            "completeness": 95.00,
            "missing_values": 5,
            "duplicate_rows": 2,
            "validation_issues": 3,
            "anomalies": 4,
        },
        {
            "timestamp": "2026-11-10T19:00:00+05:30",
            "dataset_name": "customer_data.csv",
            "rows": 15,
            "columns": 10,
            "quality_score": 97.72,
            "completeness": 99.33,
            "missing_values": 1,
            "duplicate_rows": 0,
            "validation_issues": 0,
            "anomalies": 1,
        },
    ]

    pd.DataFrame(history_data).to_csv(
        history_path,
        index=False,
    )

    return history_path


def test_compares_latest_two_executions(history_file):
    result = compare_quality_history(history_file)

    assert result["previous_execution"]["quality_score"] == 95.00
    assert result["latest_execution"]["quality_score"] == 97.72


def test_detects_quality_improvements(history_file):
    result = compare_quality_history(history_file)

    comparison = result["comparison"]

    assert comparison["quality_score"]["status"] == "improved"
    assert comparison["completeness"]["status"] == "improved"
    assert comparison["missing_values"]["status"] == "improved"
    assert comparison["duplicate_rows"]["status"] == "improved"
    assert comparison["validation_issues"]["status"] == "improved"
    assert comparison["anomalies"]["status"] == "improved"


def test_calculates_metric_differences(history_file):
    result = compare_quality_history(history_file)

    comparison = result["comparison"]

    assert comparison["quality_score"]["difference"] == 2.72
    assert comparison["completeness"]["difference"] == 4.33
    assert comparison["missing_values"]["difference"] == -4
    assert comparison["duplicate_rows"]["difference"] == -2


def test_detects_regressions(history_file):
    history_df = pd.read_csv(history_file)

    history_df.loc[1, "quality_score"] = 90.00
    history_df.loc[1, "missing_values"] = 8

    history_df.to_csv(history_file, index=False)

    result = compare_quality_history(history_file)

    comparison = result["comparison"]

    assert comparison["quality_score"]["status"] == "regressed"
    assert comparison["missing_values"]["status"] == "regressed"


def test_detects_unchanged_metrics(history_file):
    history_df = pd.read_csv(history_file)

    history_df.loc[1, "rows"] = history_df.loc[0, "rows"]
    history_df.loc[1, "columns"] = history_df.loc[0, "columns"]

    history_df.to_csv(history_file, index=False)

    result = compare_quality_history(history_file)

    assert result["previous_execution"]["rows"] == 15
    assert result["latest_execution"]["columns"] == 10


def test_raises_error_when_history_file_missing(tmp_path):
    missing_path = tmp_path / "missing_history.csv"

    with pytest.raises(FileNotFoundError):
        compare_quality_history(missing_path)


def test_raises_error_when_only_one_execution_exists(tmp_path):
    history_path = tmp_path / "quality_history.csv"

    pd.DataFrame([
        {
            "timestamp": "2026-11-10T18:00:00+05:30",
            "dataset_name": "customer_data.csv",
            "rows": 15,
            "columns": 10,
            "quality_score": 95.00,
            "completeness": 95.00,
            "missing_values": 5,
            "duplicate_rows": 2,
            "validation_issues": 3,
            "anomalies": 4,
        }
    ]).to_csv(history_path, index=False)

    with pytest.raises(ValueError, match="At least two executions"):
        compare_quality_history(history_path)


def test_raises_error_for_missing_columns(tmp_path):
    history_path = tmp_path / "quality_history.csv"

    pd.DataFrame({
        "timestamp": [
            "2026-11-10T18:00:00+05:30",
            "2026-11-10T19:00:00+05:30",
        ],
        "quality_score": [95.0, 97.0],
    }).to_csv(history_path, index=False)

    with pytest.raises(ValueError, match="missing columns"):
        compare_quality_history(history_path)
