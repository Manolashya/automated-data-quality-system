import pandas as pd
import pytest

from src.history.risk_comparator import compare_dataset_risks


def make_history():
    return pd.DataFrame([
        {
            "timestamp": "2026-11-20 10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 25,
            "risk_level": "Medium",
        },
        {
            "timestamp": "2026-11-21 10:00:00",
            "dataset_name": "customers.csv",
            "risk_score": 55,
            "risk_level": "High",
        },
        {
            "timestamp": "2026-11-21 11:00:00",
            "dataset_name": "employees.csv",
            "risk_score": 10,
            "risk_level": "Low",
        },
        {
            "timestamp": "2026-11-21 12:00:00",
            "dataset_name": "orders.csv",
            "risk_score": 85,
            "risk_level": "Critical",
        },
    ])


def test_empty_history_returns_empty_dataframe():
    result = compare_dataset_risks(pd.DataFrame())

    assert result.empty
    assert "dataset_name" in result.columns


def test_latest_record_is_selected_for_each_dataset():
    result = compare_dataset_risks(make_history())

    customers = result[
        result["dataset_name"] == "customers.csv"
    ]

    assert len(customers) == 1
    assert customers.iloc[0]["risk_score"] == 55


def test_results_are_sorted_by_risk_score_descending():
    result = compare_dataset_risks(make_history())

    assert result["risk_score"].tolist() == [85, 55, 10]


def test_missing_risk_level_is_calculated():
    history = pd.DataFrame([
        {
            "timestamp": "2026-11-21 10:00:00",
            "dataset_name": "new_dataset.csv",
            "risk_score": 75,
            "risk_level": "",
        }
    ])

    result = compare_dataset_risks(history)

    assert result.iloc[0]["risk_level"] == "Critical"


def test_invalid_records_are_excluded():
    history = pd.DataFrame([
        {
            "timestamp": "2026-11-21 10:00:00",
            "dataset_name": "valid.csv",
            "risk_score": 30,
            "risk_level": "Medium",
        },
        {
            "timestamp": "invalid-date",
            "dataset_name": "bad_date.csv",
            "risk_score": 50,
            "risk_level": "High",
        },
        {
            "timestamp": "2026-11-21 10:00:00",
            "dataset_name": "bad_score.csv",
            "risk_score": 150,
            "risk_level": "Critical",
        },
    ])

    result = compare_dataset_risks(history)

    assert result["dataset_name"].tolist() == ["valid.csv"]


def test_missing_required_column_raises_error():
    history = pd.DataFrame({
        "dataset_name": ["customers.csv"],
        "risk_score": [30],
    })

    with pytest.raises(ValueError, match="missing required columns"):
        compare_dataset_risks(history)


def test_risk_levels_are_calculated_at_correct_thresholds():
    history = pd.DataFrame([
        {
            "timestamp": "2026-11-21 10:00:00",
            "dataset_name": "low.csv",
            "risk_score": 15,
            "risk_level": "",
        },
        {
            "timestamp": "2026-11-21 10:01:00",
            "dataset_name": "medium.csv",
            "risk_score": 20,
            "risk_level": "",
        },
        {
            "timestamp": "2026-11-21 10:02:00",
            "dataset_name": "high.csv",
            "risk_score": 40,
            "risk_level": "",
        },
        {
            "timestamp": "2026-11-21 10:03:00",
            "dataset_name": "critical.csv",
            "risk_score": 70,
            "risk_level": "",
        },
    ])

    result = compare_dataset_risks(history)

    levels = dict(zip(
        result["dataset_name"],
        result["risk_level"]
    ))

    assert levels["low.csv"] == "Low"
    assert levels["medium.csv"] == "Medium"
    assert levels["high.csv"] == "High"
    assert levels["critical.csv"] == "Critical"
