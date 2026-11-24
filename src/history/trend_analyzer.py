
import pandas as pd


REQUIRED_COLUMNS = [
    "timestamp",
    "dataset_name",
    "quality_score",
    "completeness",
    "missing_values",
    "duplicate_rows",
    "validation_issues",
    "anomalies",
]


def analyze_quality_trends(history, dataset_name=None):
    """
    Analyze historical quality trends for a dataset.

    Returns quality direction, score changes, recurring issues,
    and actionable trend warnings.
    """

    if not isinstance(history, pd.DataFrame):
        raise TypeError("history must be a pandas DataFrame.")

    if history.empty:
        return {
            "status": "insufficient_data",
            "dataset_name": dataset_name,
            "execution_count": 0,
            "latest_score": None,
            "previous_score": None,
            "score_change": None,
            "trend": "Insufficient data",
            "recurring_issues": [],
            "warnings": [],
        }

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in history.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required history columns: {missing_columns}"
        )

    data = history.copy()

    if dataset_name is not None:
        data = data[
            data["dataset_name"] == dataset_name
        ].copy()

    if data.empty:
        return {
            "status": "insufficient_data",
            "dataset_name": dataset_name,
            "execution_count": 0,
            "latest_score": None,
            "previous_score": None,
            "score_change": None,
            "trend": "Insufficient data",
            "recurring_issues": [],
            "warnings": [],
        }

    data["parsed_timestamp"] = pd.to_datetime(
        data["timestamp"],
        errors="coerce",
        utc=True,
    )

    data["quality_score"] = pd.to_numeric(
        data["quality_score"],
        errors="coerce",
    )

    data = data.dropna(
        subset=["parsed_timestamp", "quality_score"]
    ).sort_values("parsed_timestamp")

    if data.empty:
        return {
            "status": "insufficient_data",
            "dataset_name": dataset_name,
            "execution_count": 0,
            "latest_score": None,
            "previous_score": None,
            "score_change": None,
            "trend": "Insufficient data",
            "recurring_issues": [],
            "warnings": [],
        }

    latest = data.iloc[-1]
    previous = data.iloc[-2] if len(data) >= 2 else None

    latest_score = float(latest["quality_score"])

    if previous is None:
        previous_score = None
        score_change = None
        trend = "Insufficient data"

    else:
        previous_score = float(previous["quality_score"])

        score_change = round(
            latest_score - previous_score,
            2,
        )

        if score_change > 0:
            trend = "Improving"
        elif score_change < 0:
            trend = "Declining"
        else:
            trend = "Stable"

    recurring_issues = []

    issue_columns = [
        "missing_values",
        "duplicate_rows",
        "validation_issues",
        "anomalies",
    ]

    for column in issue_columns:
        values = pd.to_numeric(
            data[column],
            errors="coerce",
        ).fillna(0)

        if (values > 0).sum() >= 2:
            recurring_issues.append(column)

    warnings = []

    if trend == "Declining":
        warnings.append(
            "Quality score declined compared with the previous execution."
        )

    if trend == "Stable":
        warnings.append(
            "Quality score did not change compared with the previous execution."
        )

    if recurring_issues:
        warnings.append(
            "Recurring quality problems detected: "
            + ", ".join(recurring_issues)
        )

    return {
        "status": "success",
        "dataset_name": latest["dataset_name"],
        "execution_count": len(data),
        "latest_score": latest_score,
        "previous_score": previous_score,
        "score_change": score_change,
        "trend": trend,
        "recurring_issues": recurring_issues,
        "warnings": warnings,
    }
