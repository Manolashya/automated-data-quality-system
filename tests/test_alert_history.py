
from datetime import datetime

import pytest

from src.alerts.alert_history import (
    load_alert_history,
    save_alert_history,
)


@pytest.fixture
def sample_alert():
    return {
        "metric": "Missing Values",
        "actual_value": 6.0,
        "threshold": 5.0,
        "severity": "Warning",
        "message": "Missing-value percentage exceeded threshold.",
    }


def test_save_and_load_alert(tmp_path, sample_alert):
    history_path = tmp_path / "alert_history.csv"

    saved_path = save_alert_history(
        [sample_alert],
        "customers.csv",
        history_path,
    )

    records = load_alert_history(history_path)

    assert saved_path == history_path
    assert len(records) == 1
    assert records[0]["dataset_name"] == "customers.csv"
    assert records[0]["metric"] == "Missing Values"
    assert records[0]["actual_value"] == "6.0"
    assert records[0]["threshold"] == "5.0"
    assert records[0]["severity"] == "Warning"
    assert records[0]["message"] == sample_alert["message"]
    assert datetime.fromisoformat(records[0]["timestamp"])


def test_append_multiple_alerts(tmp_path, sample_alert):
    history_path = tmp_path / "alert_history.csv"

    second_alert = {
        **sample_alert,
        "metric": "Duplicate Rows",
        "actual_value": 3.0,
        "threshold": 2.0,
    }

    save_alert_history([sample_alert], "first.csv", history_path)
    save_alert_history([second_alert], "second.csv", history_path)

    records = load_alert_history(history_path)

    assert len(records) == 2
    assert records[0]["dataset_name"] == "first.csv"
    assert records[1]["dataset_name"] == "second.csv"
    assert records[1]["metric"] == "Duplicate Rows"


def test_load_missing_file_returns_empty_list(tmp_path):
    history_path = tmp_path / "missing.csv"

    assert load_alert_history(history_path) == []


def test_load_empty_file_returns_empty_list(tmp_path):
    history_path = tmp_path / "empty.csv"
    history_path.touch()

    assert load_alert_history(history_path) == []


def test_empty_alerts_do_not_create_file(tmp_path):
    history_path = tmp_path / "alert_history.csv"

    result = save_alert_history([], "customers.csv", history_path)

    assert result == history_path
    assert not history_path.exists()


def test_non_list_alerts_raise_type_error(tmp_path):
    history_path = tmp_path / "alert_history.csv"

    with pytest.raises(TypeError, match="alerts must be a list"):
        save_alert_history(
            {"metric": "Missing Values"},
            "customers.csv",
            history_path,
        )


def test_blank_dataset_name_raises_value_error(tmp_path, sample_alert):
    history_path = tmp_path / "alert_history.csv"

    with pytest.raises(ValueError, match="dataset_name"):
        save_alert_history([sample_alert], "  ", history_path)


def test_missing_alert_field_raises_value_error(tmp_path):
    history_path = tmp_path / "alert_history.csv"
    incomplete_alert = {
        "metric": "Missing Values",
        "severity": "Warning",
    }

    with pytest.raises(ValueError, match="Missing required alert field"):
        save_alert_history(
            [incomplete_alert],
            "customers.csv",
            history_path,
        )
