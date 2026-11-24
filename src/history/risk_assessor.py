import pandas as pd

from src.history.trend_analyzer import analyze_quality_trends


REQUIRED_REPORT_FIELDS = [
    "rows",
    "column_count",
    "overall_quality_score",
    "missing_values",
    "duplicate_rows",
]

DEFAULT_THRESHOLDS = {
    "minimum_overall_score": 80.0,
    "maximum_missing_percentage": 5.0,
    "maximum_duplicate_percentage": 2.0,
}


def _get_thresholds(thresholds):
    """Accept either validated flat thresholds or the YAML config structure."""
    if not isinstance(thresholds, dict):
        raise TypeError("thresholds must be a dictionary.")

    values = thresholds.get("quality_thresholds", thresholds)

    if not isinstance(values, dict):
        raise ValueError("Invalid quality threshold configuration.")

    result = DEFAULT_THRESHOLDS.copy()

    for key in result:
        if key in values:
            result[key] = float(values[key])

    for key, value in result.items():
        if not 0 <= value <= 100:
            raise ValueError(f"{key} must be between 0 and 100.")

    return result


def _risk_level(score):
    """Convert a numeric risk score into a readable risk category."""
    if score >= 70:
        return "Critical"
    if score >= 40:
        return "High"
    if score >= 20:
        return "Medium"
    return "Low"


def assess_quality_risk(
    profiling_report,
    history,
    thresholds,
    dataset_name=None,
):
    """
    Assess dataset quality risk using transparent, rule-based scoring.

    This is an explainable early-warning assessment, not an ML prediction.
    """

    if not isinstance(profiling_report, dict):
        raise TypeError("profiling_report must be a dictionary.")

    if not isinstance(history, pd.DataFrame):
        raise TypeError("history must be a pandas DataFrame.")

    missing_fields = [
        field for field in REQUIRED_REPORT_FIELDS
        if field not in profiling_report
    ]

    if missing_fields:
        raise ValueError(
            f"Missing required profiling fields: {missing_fields}"
        )

    config = _get_thresholds(thresholds)

    rows = int(profiling_report["rows"])
    columns = int(profiling_report["column_count"])
    quality_score = float(profiling_report["overall_quality_score"])
    duplicate_rows = int(profiling_report["duplicate_rows"])
    missing_values = profiling_report["missing_values"]

    if rows <= 0 or columns <= 0:
        raise ValueError("Dataset rows and columns must be positive.")

    if not 0 <= quality_score <= 100:
        raise ValueError("overall_quality_score must be between 0 and 100.")

    if isinstance(missing_values, dict):
        total_missing = sum(
            int(value) for value in missing_values.values()
        )
    else:
        total_missing = int(missing_values)

    if total_missing < 0 or duplicate_rows < 0:
        raise ValueError("Missing and duplicate counts cannot be negative.")

    missing_percentage = (
        total_missing / (rows * columns)
    ) * 100

    duplicate_percentage = (
        duplicate_rows / rows
    ) * 100

    if dataset_name is None:
        dataset_name = profiling_report.get("file_name")

    trend = analyze_quality_trends(
        history,
        dataset_name=dataset_name,
    )

    risk_score = 0.0
    factors = []
    warnings = []
    recommendations = []

    # Rule 1: Current overall quality score.
    minimum_score = config["minimum_overall_score"]

    if quality_score < minimum_score:
        points = min(
            30.0,
            (minimum_score - quality_score) * 1.5,
        )
        risk_score += points
        factors.append({
            "factor": "Low overall quality score",
            "points": round(points, 2),
        })
        warnings.append(
            f"Quality score {quality_score:.2f}% is below "
            f"the configured minimum of {minimum_score:.2f}%."
        )
        recommendations.append(
            "Investigate profiling and validation issues to improve "
            "the overall quality score."
        )

    # Rule 2: Missing-value percentage.
    maximum_missing = config["maximum_missing_percentage"]

    if missing_percentage > maximum_missing:
        points = min(
            20.0,
            (missing_percentage - maximum_missing) * 4,
        )
        risk_score += points
        factors.append({
            "factor": "Missing-value threshold exceeded",
            "points": round(points, 2),
        })
        warnings.append(
            f"Missing-value percentage {missing_percentage:.2f}% "
            f"exceeds the configured limit of {maximum_missing:.2f}%."
        )
        recommendations.append(
            "Investigate missing fields and apply suitable "
            "missing-value handling rules."
        )

    # Rule 3: Duplicate-row percentage.
    maximum_duplicates = config["maximum_duplicate_percentage"]

    if duplicate_percentage > maximum_duplicates:
        points = min(
            15.0,
            (duplicate_percentage - maximum_duplicates) * 5,
        )
        risk_score += points
        factors.append({
            "factor": "Duplicate-row threshold exceeded",
            "points": round(points, 2),
        })
        warnings.append(
            f"Duplicate percentage {duplicate_percentage:.2f}% "
            f"exceeds the configured limit of "
            f"{maximum_duplicates:.2f}%."
        )
        recommendations.append(
            "Review duplicate records and apply an appropriate "
            "deduplication strategy."
        )

    # Rule 4: Recent quality trend.
    if trend["trend"] == "Declining":
        change = trend["score_change"]

        points = 15.0 if change <= -5 else 10.0
        risk_score += points

        factors.append({
            "factor": "Declining quality trend",
            "points": points,
        })
        warnings.append(
            f"Quality score declined by {abs(change):.2f} points "
            "in the latest execution."
        )
        recommendations.append(
            "Investigate recent changes in the dataset and monitor "
            "the next quality executions."
        )

    # Rule 5: Repeated issues in historical executions.
    recurring_issues = trend["recurring_issues"]

    if recurring_issues:
        points = min(
            20.0,
            len(recurring_issues) * 5.0,
        )
        risk_score += points

        factors.append({
            "factor": "Recurring historical issues",
            "points": points,
        })
        warnings.append(
            "Recurring issues detected: "
            + ", ".join(recurring_issues)
            + "."
        )
        recommendations.append(
            "Investigate recurring issues at their source instead "
            "of repeatedly correcting individual executions."
        )

    risk_score = round(min(100.0, risk_score), 2)

    if not warnings:
        warnings.append(
            "No significant quality risk indicators were detected."
        )
        recommendations.append(
            "Continue monitoring quality scores and historical trends."
        )

    return {
        "dataset_name": dataset_name,
        "risk_score": risk_score,
        "risk_level": _risk_level(risk_score),
        "quality_score": round(quality_score, 2),
        "missing_percentage": round(missing_percentage, 2),
        "duplicate_percentage": round(duplicate_percentage, 2),
        "trend": trend["trend"],
        "recurring_issues": recurring_issues,
        "factors": factors,
        "warnings": warnings,
        "recommendations": recommendations,
    }
