import pandas as pd


REQUIRED_COLUMNS = [
    "timestamp",
    "dataset_name",
    "risk_score",
]

OUTPUT_COLUMNS = [
    "timestamp",
    "dataset_name",
    "risk_score",
    "risk_level",
    "parsed_timestamp",
]


def _get_risk_level(score):
    """Convert a risk score into its corresponding risk level."""

    if score < 20:
        return "Low"
    elif score < 40:
        return "Medium"
    elif score < 70:
        return "High"
    else:
        return "Critical"


def compare_dataset_risks(history):
    """
    Return the latest valid risk record for every dataset.

    Older executions are excluded from the comparison.
    Results are sorted from highest risk to lowest risk.
    """

    if not isinstance(history, pd.DataFrame):
        raise TypeError("Risk history must be a pandas DataFrame.")

    if history.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in history.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Risk history is missing required columns: {missing_columns}"
        )

    data = history.copy()

    data["parsed_timestamp"] = pd.to_datetime(
        data["timestamp"],
        errors="coerce",
        utc=True
    )

    data["risk_score"] = pd.to_numeric(
        data["risk_score"],
        errors="coerce"
    )

    data["dataset_name"] = (
        data["dataset_name"]
        .astype("string")
        .str.strip()
    )

    data = data.dropna(
        subset=[
            "parsed_timestamp",
            "risk_score",
            "dataset_name",
        ]
    )

    data = data[
        data["dataset_name"].ne("")
        & data["risk_score"].between(0, 100)
    ]

    if data.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    data = data.sort_values(
        "parsed_timestamp",
        kind="stable"
    )

    latest_records = data.drop_duplicates(
        subset=["dataset_name"],
        keep="last"
    ).copy()

    if "risk_level" not in latest_records.columns:
        latest_records["risk_level"] = ""

    latest_records["risk_level"] = (
        latest_records["risk_level"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    missing_levels = latest_records["risk_level"] == ""

    latest_records.loc[missing_levels, "risk_level"] = (
        latest_records.loc[missing_levels, "risk_score"]
        .apply(_get_risk_level)
    )

    latest_records = latest_records.sort_values(
        "risk_score",
        ascending=False,
        kind="stable"
    )

    return latest_records.reset_index(drop=True)
