import pandas as pd


REQUIRED_COLUMNS = [
    "timestamp",
    "dataset_name",
    "risk_score",
]


def _insufficient_result(dataset_name, execution_count=0):
    return {
        "status": "insufficient_data",
        "dataset_name": dataset_name,
        "execution_count": execution_count,
        "latest_score": None,
        "previous_score": None,
        "score_change": None,
        "trend": "Insufficient data",
        "warnings": [],
    }


def analyze_risk_trends(
    history,
    dataset_name=None,
    stable_threshold=1.0
):
    """
    Analyze historical risk-score changes for one dataset.

    A decreasing risk score means improving conditions.
    An increasing risk score means worsening conditions.
    """

    if not isinstance(history, pd.DataFrame):
        raise TypeError("history must be a pandas DataFrame.")

    if not isinstance(stable_threshold, (int, float)):
        raise TypeError("stable_threshold must be numeric.")

    if stable_threshold < 0:
        raise ValueError("stable_threshold cannot be negative.")

    if history.empty:
        return _insufficient_result(dataset_name)

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in history.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required risk history columns: {missing_columns}"
        )

    data = history.copy()

    if dataset_name is not None:
        data = data[
            data["dataset_name"] == dataset_name
        ].copy()

    if data.empty:
        return _insufficient_result(dataset_name)

    data["parsed_timestamp"] = pd.to_datetime(
        data["timestamp"],
        errors="coerce",
        utc=True
    )

    data["risk_score"] = pd.to_numeric(
        data["risk_score"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["parsed_timestamp", "risk_score"]
    )

    data = data[
        data["risk_score"].between(0, 100)
    ].sort_values("parsed_timestamp")

    if data.empty:
        return _insufficient_result(dataset_name)

    latest = data.iloc[-1]
    latest_score = float(latest["risk_score"])

    if len(data) < 2:
        result = _insufficient_result(
            latest["dataset_name"],
            execution_count=len(data)
        )
        result["latest_score"] = latest_score
        return result

    previous = data.iloc[-2]
    previous_score = float(previous["risk_score"])

    score_change = round(
        latest_score - previous_score,
        2
    )

    if score_change < -stable_threshold:
        trend = "Improving"
    elif score_change > stable_threshold:
        trend = "Worsening"
    else:
        trend = "Stable"

    warnings = []

    if trend == "Improving":
        warnings.append(
            "Risk score decreased compared with the previous execution."
        )
    elif trend == "Worsening":
        warnings.append(
            "Risk score increased compared with the previous execution."
        )
    else:
        warnings.append(
            "Risk score remained relatively stable."
        )

    return {
        "status": "success",
        "dataset_name": latest["dataset_name"],
        "execution_count": len(data),
        "latest_score": latest_score,
        "previous_score": previous_score,
        "score_change": score_change,
        "trend": trend,
        "warnings": warnings,
    }
