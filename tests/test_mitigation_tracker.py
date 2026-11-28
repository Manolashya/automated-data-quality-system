import pandas as pd
import pytest

from src.history.mitigation_tracker import (
    MITIGATION_FIELDS,
    generate_mitigation_actions,
    load_mitigation_actions,
    update_mitigation_status,
)


def make_risk_result(**overrides):
    result = {
        "dataset_name": "customers.csv",
        "risk_level": "High",
        "recommendations": [
            "Investigate missing fields.",
            "Review duplicate records.",
        ],
    }
    result.update(overrides)
    return result


def test_load_returns_empty_dataframe_when_file_is_missing(tmp_path):
    path = tmp_path / "actions.csv"

    actions = load_mitigation_actions(path)

    assert actions.empty
    assert list(actions.columns) == MITIGATION_FIELDS


@pytest.mark.parametrize(
    ("risk_level", "expected_priority"),
    [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Critical", "Urgent"),
    ],
)
def test_generate_actions_assigns_priority(
    tmp_path,
    risk_level,
    expected_priority,
):
    path = tmp_path / "actions.csv"

    created = generate_mitigation_actions(
        make_risk_result(risk_level=risk_level),
        path,
    )

    assert len(created) == 2
    assert set(created["priority"]) == {expected_priority}
    assert set(created["status"]) == {"Pending"}
    assert path.exists()


def test_generated_actions_are_saved_and_loaded(tmp_path):
    path = tmp_path / "actions.csv"

    created = generate_mitigation_actions(
        make_risk_result(),
        path,
    )

    loaded = load_mitigation_actions(path)

    assert len(loaded) == 2
    assert list(loaded.columns) == MITIGATION_FIELDS
    assert set(loaded["action_id"]) == set(created["action_id"])


def test_repeated_generation_does_not_duplicate_open_actions(tmp_path):
    path = tmp_path / "actions.csv"
    risk_result = make_risk_result()

    first = generate_mitigation_actions(risk_result, path)
    second = generate_mitigation_actions(risk_result, path)

    assert len(first) == 2
    assert second.empty
    assert len(load_mitigation_actions(path)) == 2


def test_duplicate_recommendations_in_one_result_create_one_action(tmp_path):
    path = tmp_path / "actions.csv"

    created = generate_mitigation_actions(
        make_risk_result(
            recommendations=[
                "Investigate missing fields.",
                "Investigate missing fields.",
            ]
        ),
        path,
    )

    assert len(created) == 1


def test_completed_action_can_be_generated_again(tmp_path):
    path = tmp_path / "actions.csv"
    risk_result = make_risk_result()

    created = generate_mitigation_actions(risk_result, path)

    update_mitigation_status(
        created.iloc[0]["action_id"],
        "Completed",
        path,
    )

    regenerated = generate_mitigation_actions(risk_result, path)

    assert len(regenerated) == 1
    assert len(load_mitigation_actions(path)) == 3


def test_update_mitigation_status_persists_change(tmp_path):
    path = tmp_path / "actions.csv"

    created = generate_mitigation_actions(
        make_risk_result(),
        path,
    )

    action_id = created.iloc[0]["action_id"]

    updated = update_mitigation_status(
        action_id,
        "In Progress",
        path,
    )

    loaded = load_mitigation_actions(path)

    saved = loaded[loaded["action_id"] == action_id].iloc[0]

    assert updated["status"] == "In Progress"
    assert saved["status"] == "In Progress"
    assert saved["updated_at"]


def test_update_rejects_invalid_status(tmp_path):
    path = tmp_path / "actions.csv"

    created = generate_mitigation_actions(
        make_risk_result(),
        path,
    )

    with pytest.raises(ValueError, match="Status must be"):
        update_mitigation_status(
            created.iloc[0]["action_id"],
            "Started",
            path,
        )


def test_update_rejects_unknown_action_id(tmp_path):
    path = tmp_path / "actions.csv"

    generate_mitigation_actions(make_risk_result(), path)

    with pytest.raises(ValueError, match="was not found"):
        update_mitigation_status(
            "unknown-id",
            "Completed",
            path,
        )


@pytest.mark.parametrize(
    ("risk_result", "error", "message"),
    [
        ([], TypeError, "risk_result must be a dictionary"),
        (
            make_risk_result(dataset_name=""),
            ValueError,
            "dataset_name is required",
        ),
        (
            make_risk_result(risk_level="Unknown"),
            ValueError,
            "Invalid risk level",
        ),
        (
            make_risk_result(recommendations="not a list"),
            TypeError,
            "recommendations must be a list",
        ),
        (
            make_risk_result(recommendations=[""]),
            ValueError,
            "Recommendations cannot be empty",
        ),
    ],
)
def test_generate_rejects_invalid_risk_results(
    tmp_path,
    risk_result,
    error,
    message,
):
    with pytest.raises(error, match=message):
        generate_mitigation_actions(
            risk_result,
            tmp_path / "actions.csv",
        )


def test_generate_rejects_non_string_recommendation(tmp_path):
    with pytest.raises(TypeError, match="must be a string"):
        generate_mitigation_actions(
            make_risk_result(recommendations=[123]),
            tmp_path / "actions.csv",
        )


def test_load_rejects_csv_with_missing_columns(tmp_path):
    path = tmp_path / "actions.csv"
    pd.DataFrame({"action_id": ["one"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="missing columns"):
        load_mitigation_actions(path)
