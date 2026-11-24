import pandas as pd
import pytest

from src.history.risk_assessor import assess_quality_risk


THRESHOLDS = {
    "minimum_overall_score": 80.0,
    "maximum_missing_percentage": 5.0,
    "maximum_duplicate_percentage": 2.0,
}


def create_report(
    quality_score=95.0,
    missing_values=None,
    duplicate_rows=0,
):
    return {
        "file_name": "customers.csv",
        "rows": 100,
        "column_count": 10,
        "overall_quality_score": quality_score,
        "missing_values": missing_values or {},
        "duplicate_rows": duplicate_rows,
    }


def create_history(scores, missing=None, duplicates=None):
    records = []

    for index, score in enumerate(scores):
        records.append({
            "timestamp": (
                f"2026-11-{20 + index:02d}T10:00:00+05:30"
            ),
            "dataset_name": "customers.csv",
            "quality_score": score,
            "completeness": 99.0,
            "missing_values": (
                missing[index] if missing else 0
            ),
            "duplicate_rows": (
                duplicates[index] if duplicates else 0
            ),
            "validation_issues": 0,
            "anomalies": 0,
        })

    return pd.DataFrame(records)


def test_healthy_dataset_has_low_risk():
    result = assess_quality_risk(
        create_report(),
        create_history([95, 95]),
        THRESHOLDS,
    )

    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"
    assert result["trend"] == "Stable"


def test_low_quality_score_increases_risk():
    result = assess_quality_risk(
        create_report(quality_score=60),
        create_history([60, 60]),
        THRESHOLDS,
    )

    assert result["risk_score"] == 30
    assert result["risk_level"] == "Medium"
    assert any(
        "Low overall quality score" in item["factor"]
        for item in result["factors"]
    )


def test_missing_value_threshold_breach_increases_risk():
    result = assess_quality_risk(
        create_report(missing_values={"email": 100}),
        create_history([95, 95]),
        THRESHOLDS,
    )

    assert result["missing_percentage"] == 10.0
    assert result["risk_score"] == 20
    assert result["risk_level"] == "Medium"


def test_duplicate_threshold_breach_increases_risk():
    result = assess_quality_risk(
        create_report(duplicate_rows=10),
        create_history([95, 95]),
        THRESHOLDS,
    )

    assert result["duplicate_percentage"] == 10.0
    assert result["risk_score"] == 15
    assert result["risk_level"] == "Low"


def test_declining_trend_increases_risk():
    result = assess_quality_risk(
        create_report(),
        create_history([98, 90]),
        THRESHOLDS,
    )

    assert result["trend"] == "Declining"
    assert result["risk_score"] == 15
    assert result["risk_level"] == "Low"


def test_small_decline_adds_ten_points():
    result = assess_quality_risk(
        create_report(),
        create_history([95, 92]),
        THRESHOLDS,
    )

    assert result["risk_score"] == 10


def test_recurring_issues_increase_risk():
    history = create_history([95, 95])
    history["missing_values"] = [1, 1]
    history["validation_issues"] = [2, 2]

    result = assess_quality_risk(
        create_report(),
        history,
        THRESHOLDS,
    )

    assert "missing_values" in result["recurring_issues"]
    assert "validation_issues" in result["recurring_issues"]
    assert result["risk_score"] == 10


def test_risk_score_is_capped_at_one_hundred():
    result = assess_quality_risk(
        create_report(
            quality_score=0,
            missing_values={"email": 1000},
            duplicate_rows=100,
        ),
        create_history([95, 80]),
        THRESHOLDS,
    )

    assert result["risk_score"] <= 100


def test_nested_threshold_configuration_is_supported():
    result = assess_quality_risk(
        create_report(),
        create_history([95, 95]),
        {"quality_thresholds": THRESHOLDS},
    )

    assert result["risk_level"] == "Low"


def test_dataset_name_filter_is_respected():
    history = create_history([95, 95])

    other = create_history([98, 90])
    other["dataset_name"] = "sales.csv"

    combined = pd.concat(
        [history, other],
        ignore_index=True,
    )

    result = assess_quality_risk(
        create_report(),
        combined,
        THRESHOLDS,
    )

    assert result["dataset_name"] == "customers.csv"
    assert result["trend"] == "Stable"


def test_invalid_report_type():
    with pytest.raises(TypeError):
        assess_quality_risk(
            [],
            create_history([95, 95]),
            THRESHOLDS,
        )


def test_invalid_history_type():
    with pytest.raises(TypeError):
        assess_quality_risk(
            create_report(),
            [],
            THRESHOLDS,
        )


def test_missing_report_field():
    report = create_report()
    del report["rows"]

    with pytest.raises(ValueError, match="Missing required profiling fields"):
        assess_quality_risk(
            report,
            create_history([95, 95]),
            THRESHOLDS,
        )


def test_zero_row_dataset_is_rejected():
    report = create_report()
    report["rows"] = 0

    with pytest.raises(ValueError, match="must be positive"):
        assess_quality_risk(
            report,
            create_history([95, 95]),
            THRESHOLDS,
        )


def test_invalid_threshold_is_rejected():
    invalid_thresholds = THRESHOLDS.copy()
    invalid_thresholds["minimum_overall_score"] = 120

    with pytest.raises(ValueError, match="between 0 and 100"):
        assess_quality_risk(
            create_report(),
            create_history([95, 95]),
            invalid_thresholds,
        )


def test_result_contains_explanations_and_recommendations():
    result = assess_quality_risk(
        create_report(quality_score=60),
        create_history([60, 60]),
        THRESHOLDS,
    )

    assert result["factors"]
    assert result["warnings"]
    assert result["recommendations"]
    assert result["risk_level"] in [
        "Low", "Medium", "High", "Critical"
    ]
