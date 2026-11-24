
import pytest

from src.alerts.alert_insights import generate_alert_insights


def test_empty_history_returns_no_insights():
    assert generate_alert_insights([]) == []


def test_critical_alert_generates_high_priority_insight():
    history = [
        {
            "timestamp": "2026-11-24T10:00:00",
            "dataset_name": "customers.csv",
            "metric": "Overall Quality Score",
            "severity": "Critical",
        }
    ]

    insights = generate_alert_insights(history)

    critical = next(
        item for item in insights
        if item["title"] == "Critical quality alerts detected"
    )

    assert critical["priority"] == "High"
    assert "1 critical alert" in critical["finding"]


def test_missing_values_generates_recommendation():
    history = [
        {
            "timestamp": "2026-11-24T10:00:00",
            "dataset_name": "customers.csv",
            "metric": "Missing Values",
            "severity": "Warning",
        }
    ]

    insights = generate_alert_insights(history)

    metric_insight = next(
        item for item in insights
        if item["title"] == "Most frequently affected metric"
    )

    assert "Missing Values" in metric_insight["finding"]
    assert "missing values" in metric_insight["recommendation"]


def test_duplicate_rows_generates_recommendation():
    history = [
        {
            "timestamp": "2026-11-24T10:00:00",
            "dataset_name": "sales.csv",
            "metric": "Duplicate Rows",
            "severity": "Warning",
        }
    ]

    insights = generate_alert_insights(history)

    metric_insight = next(
        item for item in insights
        if item["title"] == "Most frequently affected metric"
    )

    assert "duplicate records" in metric_insight["recommendation"]


def test_repeated_dataset_generates_insight():
    history = [
        {
            "timestamp": "2026-11-24T10:00:00",
            "dataset_name": "customers.csv",
            "metric": "Missing Values",
            "severity": "Warning",
        },
        {
            "timestamp": "2026-11-24T11:00:00",
            "dataset_name": "customers.csv",
            "metric": "Duplicate Rows",
            "severity": "Warning",
        },
    ]

    insights = generate_alert_insights(history)

    dataset_insight = next(
        item for item in insights
        if item["title"] == "Repeated alerts for one dataset"
    )

    assert "customers.csv" in dataset_insight["finding"]
    assert dataset_insight["priority"] == "Medium"


def test_single_dataset_alert_does_not_generate_repeated_insight():
    history = [
        {
            "timestamp": "2026-11-24T10:00:00",
            "dataset_name": "customers.csv",
            "metric": "Missing Values",
            "severity": "Warning",
        }
    ]

    insights = generate_alert_insights(history)

    assert not any(
        item["title"] == "Repeated alerts for one dataset"
        for item in insights
    )


def test_unknown_metric_generates_fallback_recommendation():
    history = [
        {
            "timestamp": "2026-11-24T10:00:00",
            "dataset_name": "customers.csv",
            "metric": "Unknown Metric",
            "severity": "Warning",
        }
    ]

    insights = generate_alert_insights(history)

    metric_insight = next(
        item for item in insights
        if item["title"] == "Most frequently affected metric"
    )

    assert "validation rules" in metric_insight["recommendation"]


def test_invalid_history_type_raises_type_error():
    with pytest.raises(TypeError):
        generate_alert_insights("invalid")


def test_every_insight_has_required_fields():
    history = [
        {
            "timestamp": "2026-11-24T10:00:00",
            "dataset_name": "customers.csv",
            "metric": "Missing Values",
            "severity": "Critical",
        },
        {
            "timestamp": "2026-11-24T11:00:00",
            "dataset_name": "customers.csv",
            "metric": "Missing Values",
            "severity": "Warning",
        },
    ]

    insights = generate_alert_insights(history)

    for insight in insights:
        assert set(insight) == {
            "priority",
            "title",
            "finding",
            "recommendation",
        }
