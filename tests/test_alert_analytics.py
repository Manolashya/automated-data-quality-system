
import pytest

from src.alerts.alert_analytics import analyze_alert_history


def test_analyze_alert_history_basic_counts():
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
            "metric": "Overall Quality Score",
            "severity": "Critical",
        },
        {
            "timestamp": "2026-11-23T09:00:00",
            "dataset_name": "sales.csv",
            "metric": "Missing Values",
            "severity": "Warning",
        },
    ]

    result = analyze_alert_history(history)

    assert result["total_alerts"] == 3
    assert result["severity_counts"] == {
        "Warning": 2,
        "Critical": 1,
    }
    assert result["metric_counts"] == {
        "Missing Values": 2,
        "Overall Quality Score": 1,
    }
    assert result["dataset_counts"] == {
        "customers.csv": 2,
        "sales.csv": 1,
    }
    assert result["daily_counts"] == {
        "2026-11-23": 1,
        "2026-11-24": 2,
    }


def test_empty_alert_history():
    result = analyze_alert_history([])

    assert result == {
        "total_alerts": 0,
        "severity_counts": {},
        "metric_counts": {},
        "dataset_counts": {},
        "daily_counts": {},
    }


def test_counts_are_sorted_with_alphabetical_tiebreak():
    history = [
        {
            "timestamp": "2026-11-24T10:00:00",
            "dataset_name": "sales.csv",
            "metric": "Missing Values",
            "severity": "Warning",
        },
        {
            "timestamp": "2026-11-24T11:00:00",
            "dataset_name": "customers.csv",
            "metric": "Duplicate Rows",
            "severity": "Critical",
        },
        {
            "timestamp": "2026-11-24T12:00:00",
            "dataset_name": "sales.csv",
            "metric": "Missing Values",
            "severity": "Warning",
        },
        {
            "timestamp": "2026-11-24T13:00:00",
            "dataset_name": "customers.csv",
            "metric": "Duplicate Rows",
            "severity": "Critical",
        },
    ]

    result = analyze_alert_history(history)

    assert list(result["severity_counts"].items()) == [
        ("Critical", 2),
        ("Warning", 2),
    ]

    assert list(result["dataset_counts"].items()) == [
        ("customers.csv", 2),
        ("sales.csv", 2),
    ]

    assert list(result["metric_counts"].items()) == [
        ("Duplicate Rows", 2),
        ("Missing Values", 2),
    ]


def test_missing_fields_use_unknown():
    history = [
        {},
        {
            "timestamp": "invalid-timestamp",
            "dataset_name": "",
            "metric": None,
            "severity": None,
        },
    ]

    result = analyze_alert_history(history)

    assert result["severity_counts"] == {"Unknown": 2}
    assert result["metric_counts"] == {"Unknown": 2}
    assert result["dataset_counts"] == {"Unknown": 2}
    assert result["daily_counts"] == {"Unknown": 2}


def test_invalid_history_type_raises_type_error():
    with pytest.raises(TypeError, match="alert_history must be a list"):
        analyze_alert_history("invalid")


def test_invalid_record_type_raises_type_error():
    with pytest.raises(
        TypeError,
        match="Every alert history record must be a dictionary",
    ):
        analyze_alert_history([{"severity": "Warning"}, "invalid"])


def test_timezone_aware_timestamps_are_supported():
    history = [
        {
            "timestamp": "2026-11-24T10:00:00+05:30",
            "dataset_name": "customers.csv",
            "metric": "Missing Values",
            "severity": "Warning",
        }
    ]

    result = analyze_alert_history(history)

    assert result["daily_counts"] == {"2026-11-24": 1}


def test_unknown_date_is_sorted_after_valid_dates():
    history = [
        {"timestamp": "invalid"},
        {"timestamp": "2026-11-23T10:00:00"},
        {"timestamp": "2026-11-24T10:00:00"},
    ]

    result = analyze_alert_history(history)

    assert list(result["daily_counts"].keys()) == [
        "2026-11-23",
        "2026-11-24",
        "Unknown",
    ]

