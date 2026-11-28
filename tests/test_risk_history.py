import pandas as pd
import pytest

from src.history.risk_history import (
    RISK_HISTORY_FIELDS,
    save_risk_history,
    load_risk_history,
)
from src.history.risk_trend_analyzer import analyze_risk_trends


def make_risk_result(**overrides):
    result = {
        "dataset_name": "customers.csv",
        "risk_score": 35.0,
        "risk_level": "Medium",
        "quality_score": 85.0,
        "missing_percentage": 2.0,
        "duplicate_percentage": 1.0,
        "trend": "Stable",
        "recurring_issues": ["missing_values"],
    }
    result.update(overrides)
    return result


def make_history(records):
    return pd.DataFrame(records)


def test_save_creates_risk_history_file(tmp_path):
    path = tmp_path / "risk_history.csv"

    saved_path = save_risk_history(
        make_risk_result(),
        path
    )

    assert saved_path == path
    assert path.exists()

    history = load_risk_history(path)

    assert len(history) == 1
    assert list(history.columns) == RISK_HISTORY_FIELDS
    assert history.iloc[0]["dataset_name"] == "customers.csv"


def test_save_appends_multiple_risk_records(tmp_path):
    path = tmp_path / "risk_history.csv"

    save_risk_history(make_risk_result(), path)
    save_risk_history(
        make_risk_result(risk_score=25, risk_level="Medium"),
        path
    )

    history = load_risk_history(path)

    assert len(history) == 2
    assert history["risk_score"].tolist() == [35.0, 25.0]


def test_save_stores_recurring_issues_as_json(tmp_path):
    path = tmp_path / "risk_history.csv"

    save_risk_history(make_risk_result(), path)

    history = load_risk_history(path)

    assert history.iloc[0]["recurring_issues"] == (
        '["missing_values"]'
    )


def test_load_returns_empty_dataframe_when_file_missing(tmp_path):
    path = tmp_path / "missing.csv"

    history = load_risk_history(path)

    assert history.empty
    assert list(history.columns) == RISK_HISTORY_FIELDS


def test_save_rejects_non_dictionary():
    with pytest.raises(TypeError, match="risk_result"):
        save_risk_history([])


def test_save_rejects_missing_required_field(tmp_path):
    result = make_risk_result()
    del result["risk_score"]

    with pytest.raises(ValueError, match="risk_score"):
        save_risk_history(result, tmp_path / "risk.csv")


def test_save_rejects_out_of_range_risk_score(tmp_path):
    with pytest.raises(ValueError, match="risk_score"):
        save_risk_history(
            make_risk_result(risk_score=120),
            tmp_path / "risk.csv"
        )


def test_save_rejects_invalid_recurring_issues(tmp_path):
    with pytest.raises(TypeError, match="recurring_issues"):
        save_risk_history(
            make_risk_result(recurring_issues="missing_values"),
            tmp_path / "risk.csv"
        )


def test_risk_trend_is_improving_when_score_decreases():
    history = make_history([
        {
            "timestamp": "2026-11-01T10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 50,
        },
        {
            "timestamp": "2026-11-02T10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 30,
        },
    ])

    result = analyze_risk_trends(history, "customers.csv")

    assert result["trend"] == "Improving"
    assert result["score_change"] == -20


def test_risk_trend_is_worsening_when_score_increases():
    history = make_history([
        {
            "timestamp": "2026-11-01T10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 20,
        },
        {
            "timestamp": "2026-11-02T10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 45,
        },
    ])

    result = analyze_risk_trends(history, "customers.csv")

    assert result["trend"] == "Worsening"
    assert result["score_change"] == 25


def test_risk_trend_is_stable_within_threshold():
    history = make_history([
        {
            "timestamp": "2026-11-01T10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 30,
        },
        {
            "timestamp": "2026-11-02T10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 30.5,
        },
    ])

    result = analyze_risk_trends(history, "customers.csv")

    assert result["trend"] == "Stable"
    assert result["score_change"] == 0.5


def test_risk_trend_needs_two_valid_records():
    history = make_history([
        {
            "timestamp": "2026-11-01T10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 30,
        },
    ])

    result = analyze_risk_trends(history, "customers.csv")

    assert result["trend"] == "Insufficient data"
    assert result["latest_score"] == 30
    assert result["previous_score"] is None


def test_risk_trend_filters_by_dataset():
    history = make_history([
        {
            "timestamp": "2026-11-01T10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 50,
        },
        {
            "timestamp": "2026-11-02T10:00:00",
            "dataset_name": "orders.csv",
            "risk_score": 10,
        },
    ])

    result = analyze_risk_trends(history, "customers.csv")

    assert result["trend"] == "Insufficient data"
    assert result["execution_count"] == 1


def test_risk_trend_sorts_records_by_timestamp():
    history = make_history([
        {
            "timestamp": "2026-11-02T10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 20,
        },
        {
            "timestamp": "2026-11-01T10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 40,
        },
    ])

    result = analyze_risk_trends(history, "customers.csv")

    assert result["latest_score"] == 20
    assert result["previous_score"] == 40
    assert result["trend"] == "Improving"


def test_risk_trend_rejects_non_dataframe():
    with pytest.raises(TypeError, match="pandas DataFrame"):
        analyze_risk_trends([])


def test_risk_trend_rejects_missing_columns():
    history = pd.DataFrame([
        {"timestamp": "2026-11-01", "risk_score": 20}
    ])

    with pytest.raises(ValueError, match="dataset_name"):
        analyze_risk_trends(history)


def test_risk_trend_rejects_negative_stable_threshold():
    history = make_history([
        {
            "timestamp": "2026-11-01T10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 20,
        },
    ])

    with pytest.raises(ValueError, match="cannot be negative"):
        analyze_risk_trends(
            history,
            stable_threshold=-1
        )
