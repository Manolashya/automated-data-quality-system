from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MITIGATION_PATH = (
    PROJECT_ROOT / "reports" / "mitigation_actions.csv"
)

MITIGATION_FIELDS = [
    "action_id",
    "dataset_name",
    "risk_level",
    "priority",
    "recommendation",
    "status",
    "created_at",
    "updated_at",
]

VALID_RISK_LEVELS = [
    "Low",
    "Medium",
    "High",
    "Critical",
]

VALID_STATUSES = [
    "Pending",
    "In Progress",
    "Completed",
]

PRIORITY_MAP = {
    "Low": "Low",
    "Medium": "Medium",
    "High": "High",
    "Critical": "Urgent",
}


def load_mitigation_actions(actions_path=None):
    """Load saved mitigation tasks from the CSV file."""

    path = Path(actions_path or DEFAULT_MITIGATION_PATH)

    if not path.exists():
        return pd.DataFrame(columns=MITIGATION_FIELDS)

    try:
        actions = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=MITIGATION_FIELDS)

    missing_columns = [
        column
        for column in MITIGATION_FIELDS
        if column not in actions.columns
    ]

    if missing_columns:
        raise ValueError(
            "Mitigation file is missing columns: "
            + ", ".join(missing_columns)
        )

    return actions[MITIGATION_FIELDS].copy()


def generate_mitigation_actions(
    risk_result,
    actions_path=None
):
    """Create mitigation tasks from a quality risk assessment."""

    if not isinstance(risk_result, dict):
        raise TypeError("risk_result must be a dictionary")

    dataset_name = risk_result.get("dataset_name")
    risk_level = risk_result.get("risk_level")
    recommendations = risk_result.get("recommendations")

    if not isinstance(dataset_name, str) or not dataset_name.strip():
        raise ValueError("A valid dataset_name is required")

    if risk_level not in VALID_RISK_LEVELS:
        raise ValueError("Invalid risk level")

    if not isinstance(recommendations, list):
        raise TypeError("recommendations must be a list")

    for recommendation in recommendations:
        if not isinstance(recommendation, str):
            raise TypeError("Each recommendation must be a string")

        if not recommendation.strip():
            raise ValueError("Recommendations cannot be empty")

    path = Path(actions_path or DEFAULT_MITIGATION_PATH)
    actions = load_mitigation_actions(path)

    priority = PRIORITY_MAP[risk_level]
    now = datetime.now(timezone.utc).isoformat()

    new_actions = []
    seen_recommendations = set()

    for recommendation in recommendations:
        if recommendation in seen_recommendations:
            continue

        seen_recommendations.add(recommendation)

        existing_open_action = actions[
            (actions["dataset_name"] == dataset_name)
            & (actions["recommendation"] == recommendation)
            & (actions["status"].isin(["Pending", "In Progress"]))
        ]

        if not existing_open_action.empty:
            continue

        new_actions.append({
            "action_id": str(uuid4()),
            "dataset_name": dataset_name,
            "risk_level": risk_level,
            "priority": priority,
            "recommendation": recommendation,
            "status": "Pending",
            "created_at": now,
            "updated_at": now,
        })

    if new_actions:
        new_actions_df = pd.DataFrame(
            new_actions,
            columns=MITIGATION_FIELDS
        )

        actions = pd.concat(
            [actions, new_actions_df],
            ignore_index=True
        )

        path.parent.mkdir(parents=True, exist_ok=True)
        actions.to_csv(path, index=False)

    return pd.DataFrame(
        new_actions,
        columns=MITIGATION_FIELDS
    )


def update_mitigation_status(
    action_id,
    status,
    actions_path=None
):
    """Update the status of one saved mitigation task."""

    if not isinstance(action_id, str) or not action_id.strip():
        raise ValueError("A valid action_id is required")

    if status not in VALID_STATUSES:
        raise ValueError(
            "Status must be Pending, In Progress, or Completed"
        )

    path = Path(actions_path or DEFAULT_MITIGATION_PATH)
    actions = load_mitigation_actions(path)

    matching_rows = actions.index[
        actions["action_id"].astype(str) == action_id
    ]

    if len(matching_rows) == 0:
        raise ValueError("Mitigation action was not found")

    if len(matching_rows) > 1:
        raise ValueError("Duplicate mitigation action IDs were found")

    row_index = matching_rows[0]

    actions.loc[row_index, "status"] = status
    actions.loc[row_index, "updated_at"] = (
        datetime.now(timezone.utc).isoformat()
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    actions.to_csv(path, index=False)

    return actions.loc[row_index].to_dict()
