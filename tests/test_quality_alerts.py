
import pytest

from src.alerts.quality_alerts import generate_quality_alerts


@pytest.fixture
def thresholds():
    return {
        "minimum_overall_score": 80.0,
        "maximum_missing_percentage": 5.0,
        "maximum_duplicate_percentage": 2.0,
    }


@pytest.fixture
def clean_report():
    return {
        "rows": 10,
        "column_count": 5,
        "missing_values": {
            "A": 0,
            "B": 0,
            "C": 0,
            "D": 0,
            "E": 0,
        },
        "duplicate_rows": 0,
        "overall_quality_score": 100.0,
    }


def test_no_alerts_when_metrics_meet_thresholds(clean_report, thresholds):
    alerts = generate_quality_alerts(clean_report, thresholds)

    assert alerts == []


def test_low_quality_score_generates_critical_alert(clean_report, thresholds):
    clean_report["overall_quality_score"] = 70.0

    alerts = generate_quality_alerts(clean_report, thresholds)

    assert len(alerts) == 1
    assert alerts[0]["metric"] == "Overall Quality Score"
    assert alerts[0]["severity"] == "Critical"
    assert alerts[0]["actual_value"] == 70.0
    assert alerts[0]["threshold"] == 80.0


def test_excessive_missing_values_generate_warning(clean_report, thresholds):
    # 3 missing cells out of 50 total cells = 6%
    clean_report["missing_values"]["A"] = 3

    alerts = generate_quality_alerts(clean_report, thresholds)

    assert len(alerts) == 1
    assert alerts[0]["metric"] == "Missing Values"
    assert alerts[0]["severity"] == "Warning"
    assert alerts[0]["actual_value"] == 6.0


def test_excessive_duplicates_generate_warning(clean_report, thresholds):
    # 1 duplicate row out of 10 rows = 10%
    clean_report["duplicate_rows"] = 1

    alerts = generate_quality_alerts(clean_report, thresholds)

    assert len(alerts) == 1
    assert alerts[0]["metric"] == "Duplicate Rows"
    assert alerts[0]["severity"] == "Warning"
    assert alerts[0]["actual_value"] == 10.0


def test_multiple_violations_generate_multiple_alerts(clean_report, thresholds):
    clean_report["overall_quality_score"] = 70.0
    clean_report["missing_values"]["A"] = 3
    clean_report["duplicate_rows"] = 1

    alerts = generate_quality_alerts(clean_report, thresholds)

    assert len(alerts) == 3

    metrics = [alert["metric"] for alert in alerts]

    assert "Overall Quality Score" in metrics
    assert "Missing Values" in metrics
    assert "Duplicate Rows" in metrics


def test_zero_rows_raise_value_error(clean_report, thresholds):
    clean_report["rows"] = 0

    with pytest.raises(ValueError):
        generate_quality_alerts(clean_report, thresholds)


def test_zero_columns_raise_value_error(clean_report, thresholds):
    clean_report["column_count"] = 0

    with pytest.raises(ValueError):
        generate_quality_alerts(clean_report, thresholds)
