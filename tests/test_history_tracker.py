
import pandas as pd
import pytest

from src.history.history_tracker import (
    HISTORY_FIELDS,
    save_quality_history,
)


@pytest.fixture
def sample_profiling_report():
    return {
        "file_name": "customer_data.csv",
        "rows": 10,
        "column_count": 2,
        "completeness_score": {
            "Name": 100.0,
            "Age": 80.0,
        },
        "missing_values": {
            "Name": 0,
            "Age": 2,
        },
        "overall_quality_score": 90.0,
        "duplicate_rows": 1,
    }


@pytest.fixture
def sample_anomaly_results():
    return pd.DataFrame({
        "Anomaly": [
            "Normal",
            "Anomaly",
            "Normal",
            "Anomaly",
        ],
        "Anomaly_Score": [0.1, -0.5, 0.2, -0.4],
    })


def test_creates_history_csv(
    tmp_path,
    sample_profiling_report,
    sample_anomaly_results
):
    history_path = tmp_path / "quality_history.csv"

    result = save_quality_history(
        sample_profiling_report,
        [],
        sample_anomaly_results,
        history_path
    )

    assert result.exists()

    history = pd.read_csv(history_path)

    assert len(history) == 1
    assert list(history.columns) == HISTORY_FIELDS


def test_appends_multiple_records(
    tmp_path,
    sample_profiling_report,
    sample_anomaly_results
):
    history_path = tmp_path / "quality_history.csv"

    save_quality_history(
        sample_profiling_report,
        [],
        sample_anomaly_results,
        history_path
    )

    save_quality_history(
        sample_profiling_report,
        [],
        sample_anomaly_results,
        history_path
    )

    history = pd.read_csv(history_path)

    assert len(history) == 2


def test_calculates_metrics_correctly(
    tmp_path,
    sample_profiling_report,
    sample_anomaly_results
):
    history_path = tmp_path / "quality_history.csv"

    validation_issues = [
        {"rule": "email_validity"},
        {"rule": "age_range"},
    ]

    save_quality_history(
        sample_profiling_report,
        validation_issues,
        sample_anomaly_results,
        history_path
    )

    history = pd.read_csv(history_path)
    record = history.iloc[0]

    assert record["dataset_name"] == "customer_data.csv"
    assert record["rows"] == 10
    assert record["columns"] == 2
    assert record["quality_score"] == 90.0
    assert record["completeness"] == 90.0
    assert record["missing_values"] == 2
    assert record["duplicate_rows"] == 1
    assert record["validation_issues"] == 2
    assert record["anomalies"] == 2


def test_timestamp_contains_timezone(
    tmp_path,
    sample_profiling_report,
    sample_anomaly_results
):
    history_path = tmp_path / "quality_history.csv"

    save_quality_history(
        sample_profiling_report,
        [],
        sample_anomaly_results,
        history_path
    )

    history = pd.read_csv(history_path)

    timestamp = history.iloc[0]["timestamp"]

    assert "+" in timestamp or timestamp.endswith("Z")


def test_rejects_invalid_profiling_report(
    tmp_path,
    sample_anomaly_results
):
    with pytest.raises(TypeError):
        save_quality_history(
            "invalid",
            [],
            sample_anomaly_results,
            tmp_path / "quality_history.csv"
        )


def test_rejects_missing_anomaly_column(
    tmp_path,
    sample_profiling_report
):
    invalid_anomalies = pd.DataFrame({
        "Score": [0.1, 0.2]
    })

    with pytest.raises(ValueError):
        save_quality_history(
            sample_profiling_report,
            [],
            invalid_anomalies,
            tmp_path / "quality_history.csv"
        )
