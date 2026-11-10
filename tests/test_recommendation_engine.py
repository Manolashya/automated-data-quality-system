
import pandas as pd
import pytest

from src.recommendations.recommendation_engine import (
    generate_validation_recommendations,
    generate_anomaly_recommendations,
    generate_duplicate_recommendations,
    generate_drift_recommendations,
    generate_quality_regression_recommendations,
    generate_recommendations,
)


def test_validation_recommendations_group_same_issues():
    issues = [
        {"rule": "missing_value", "column": "Email"},
        {"rule": "missing_value", "column": "Email"},
        {"rule": "email_format", "column": "Email"},
    ]

    results = generate_validation_recommendations(issues)

    assert len(results) == 2

    missing = next(
        item for item in results
        if "Missing required values" in item["issue"]
    )

    assert missing["affected_count"] == 2
    assert missing["priority"] == "High"


def test_validation_recommendations_empty_input():
    assert generate_validation_recommendations([]) == []


def test_validation_recommendations_invalid_input():
    with pytest.raises(TypeError):
        generate_validation_recommendations("invalid")


def test_anomaly_recommendations_detect_anomalies():
    df = pd.DataFrame({
        "Anomaly": ["Normal", "Anomaly", "Anomaly"]
    })

    results = generate_anomaly_recommendations(df)

    assert len(results) == 1
    assert results[0]["affected_count"] == 2
    assert results[0]["priority"] == "High"


def test_anomaly_recommendations_no_anomalies():
    df = pd.DataFrame({
        "Anomaly": ["Normal", "Normal"]
    })

    assert generate_anomaly_recommendations(df) == []


def test_anomaly_recommendations_missing_column():
    df = pd.DataFrame({"Age": [20, 30]})

    with pytest.raises(ValueError):
        generate_anomaly_recommendations(df)


def test_duplicate_recommendations():
    duplicates = [
        {"row_1": 0, "row_2": 1},
        {"row_1": 2, "row_2": 3},
    ]

    results = generate_duplicate_recommendations(duplicates)

    assert len(results) == 1
    assert results[0]["affected_count"] == 2
    assert results[0]["priority"] == "Medium"


def test_duplicate_recommendations_empty_input():
    assert generate_duplicate_recommendations([]) == []


def test_drift_recommendations():
    drift = [
        {
            "column": "Age",
            "method": "PSI",
            "drift_score": 0.30,
            "drift_detected": True,
        },
        {
            "column": "Income",
            "method": "PSI",
            "drift_score": 0.15,
            "drift_detected": True,
        },
        {
            "column": "Gender",
            "method": "TVD",
            "drift_score": 0.05,
            "drift_detected": False,
        },
    ]

    results = generate_drift_recommendations(drift)

    assert len(results) == 2
    assert results[0]["priority"] == "High"
    assert results[1]["priority"] == "Medium"


def test_drift_recommendations_no_detected_drift():
    drift = [
        {
            "column": "Age",
            "method": "PSI",
            "drift_score": 0.05,
            "drift_detected": False,
        }
    ]

    assert generate_drift_recommendations(drift) == []


def test_quality_regression_recommendations():
    history = {
        "comparison": {
            "quality_score": {"status": "regressed"},
            "missing_values": {"status": "regressed"},
            "duplicate_rows": {"status": "improved"},
        }
    }

    results = generate_quality_regression_recommendations(
        history
    )

    assert len(results) == 2

    quality = next(
        item for item in results
        if "quality_score" in item["issue"]
    )

    assert quality["priority"] == "High"


def test_quality_regression_no_regression():
    history = {
        "comparison": {
            "quality_score": {"status": "improved"},
            "missing_values": {"status": "unchanged"},
        }
    }

    assert generate_quality_regression_recommendations(
        history
    ) == []


def test_combined_recommendations_priority_order():
    issues = [
        {"rule": "email_format", "column": "Email"}
    ]

    history = {
        "comparison": {
            "quality_score": {"status": "regressed"}
        }
    }

    results = generate_recommendations(
        validation_issues=issues,
        history_comparison=history,
    )

    priorities = [
        item["priority"] for item in results
    ]

    assert priorities == ["High", "Medium"]


def test_combined_recommendations_empty_input():
    assert generate_recommendations() == []
