
import pandas as pd
import pytest

from src.history.trend_analyzer import analyze_quality_trends


def create_history(scores):
    records = []

    for index, score in enumerate(scores):
        records.append({
            "timestamp": f"2026-11-{20 + index:02d}T10:00:00+05:30",
            "dataset_name": "customers.csv",
            "quality_score": score,
            "completeness": 99.0,
            "missing_values": 1,
            "duplicate_rows": 0,
            "validation_issues": 2,
            "anomalies": 0,
        })

    return pd.DataFrame(records)


def test_improving_quality_trend():
    result = analyze_quality_trends(
        create_history([90, 95])
    )

    assert result["trend"] == "Improving"
    assert result["score_change"] == 5.0
    assert result["latest_score"] == 95.0


def test_declining_quality_trend():
    result = analyze_quality_trends(
        create_history([98, 92])
    )

    assert result["trend"] == "Declining"
    assert result["score_change"] == -6.0
    assert any("declined" in warning for warning in result["warnings"])


def test_stable_quality_trend():
    result = analyze_quality_trends(
        create_history([95, 95])
    )

    assert result["trend"] == "Stable"
    assert result["score_change"] == 0.0


def test_single_execution_has_insufficient_data():
    result = analyze_quality_trends(
        create_history([95])
    )

    assert result["trend"] == "Insufficient data"
    assert result["previous_score"] is None
    assert result["score_change"] is None


def test_empty_history():
    result = analyze_quality_trends(
        pd.DataFrame()
    )

    assert result["status"] == "insufficient_data"
    assert result["execution_count"] == 0


def test_dataset_filter():
    history = create_history([90, 95])

    other = create_history([80, 85])
    other["dataset_name"] = "sales.csv"

    combined = pd.concat(
        [history, other],
        ignore_index=True,
    )

    result = analyze_quality_trends(
        combined,
        dataset_name="sales.csv",
    )

    assert result["dataset_name"] == "sales.csv"
    assert result["execution_count"] == 2
    assert result["latest_score"] == 85.0
    assert result["trend"] == "Improving"


def test_recurring_issues_are_detected():
    result = analyze_quality_trends(
        create_history([90, 95])
    )

    assert "missing_values" in result["recurring_issues"]
    assert "validation_issues" in result["recurring_issues"]


def test_invalid_input_type():
    with pytest.raises(TypeError):
        analyze_quality_trends([])


def test_missing_required_columns():
    incomplete = pd.DataFrame({
        "timestamp": ["2026-11-20T10:00:00"],
        "quality_score": [95],
    })

    with pytest.raises(ValueError, match="Missing required history columns"):
        analyze_quality_trends(incomplete)


def test_no_matching_dataset():
    result = analyze_quality_trends(
        create_history([90, 95]),
        dataset_name="unknown.csv",
    )

    assert result["status"] == "insufficient_data"
    assert result["execution_count"] == 0
