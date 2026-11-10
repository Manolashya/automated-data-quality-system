
from collections import Counter


VALIDATION_GUIDANCE = {
    "missing_value": {
        "priority": "High",
        "issue": "Missing required values",
        "recommendation": (
            "Review missing values and apply a suitable "
            "imputation strategy or obtain the correct values "
            "from the source."
        ),
    },
    "required_column": {
        "priority": "High",
        "issue": "Required column is missing",
        "recommendation": (
            "Add the missing required column and verify that "
            "the source dataset contains the expected field."
        ),
    },
    "email_format": {
        "priority": "Medium",
        "issue": "Invalid email formats",
        "recommendation": (
            "Review invalid email addresses and correct their "
            "format using the original source information."
        ),
    },
    "age_range": {
        "priority": "High",
        "issue": "Age values outside the allowed range",
        "recommendation": (
            "Verify age values against the configured minimum "
            "and maximum limits."
        ),
    },
    "numeric": {
        "priority": "Medium",
        "issue": "Non-numeric values in numeric columns",
        "recommendation": (
            "Convert valid values to numeric format and review "
            "unconvertible entries."
        ),
    },
    "non_negative": {
        "priority": "High",
        "issue": "Negative values in non-negative columns",
        "recommendation": (
            "Verify negative values and correct them using "
            "trusted source information."
        ),
    },
    "allowed_values": {
        "priority": "Medium",
        "issue": "Values outside the allowed categories",
        "recommendation": (
            "Standardize category values using the configured "
            "allowed values."
        ),
    },
}


def generate_validation_recommendations(validation_issues):
    """
    Generate grouped recommendations from validation issues.

    Args:
        validation_issues: List of validation issue dictionaries.

    Returns:
        List of structured recommendations.
    """

    if validation_issues is None:
        validation_issues = []

    if not isinstance(validation_issues, list):
        raise TypeError("Validation issues must be a list.")

    grouped_issues = Counter()

    for issue in validation_issues:

        if not isinstance(issue, dict):
            raise TypeError(
                "Each validation issue must be a dictionary."
            )

        rule = issue.get("rule")
        column = issue.get("column")

        if not rule or not column:
            continue

        grouped_issues[(rule, column)] += 1

    recommendations = []

    for (rule, column), count in grouped_issues.items():

        guidance = VALIDATION_GUIDANCE.get(rule)

        if guidance is None:
            guidance = {
                "priority": "Medium",
                "issue": "Validation rule violation",
                "recommendation": (
                    "Review the affected values and correct "
                    "them according to the validation rules."
                ),
            }

        recommendations.append({
            "category": "Validation",
            "priority": guidance["priority"],
            "issue": f"{guidance['issue']} in column '{column}'",
            "recommendation": guidance["recommendation"],
            "affected_count": count,
        })

    return recommendations

def generate_anomaly_recommendations(anomaly_results):
    """
    Generate recommendations for detected anomalies.

    Args:
        anomaly_results: DataFrame containing an Anomaly column.

    Returns:
        List of structured recommendations.
    """

    import pandas as pd

    if anomaly_results is None:
        return []

    if not isinstance(anomaly_results, pd.DataFrame):
        raise TypeError("Anomaly results must be a DataFrame.")

    if anomaly_results.empty:
        return []

    if "Anomaly" not in anomaly_results.columns:
        raise ValueError(
            "Anomaly results must contain an 'Anomaly' column."
        )

    anomaly_count = int(
        (anomaly_results["Anomaly"] == "Anomaly").sum()
    )

    if anomaly_count == 0:
        return []

    return [{
        "category": "Anomaly",
        "priority": "High",
        "issue": "Unusual records detected",
        "recommendation": (
            "Investigate the flagged records and verify unusual "
            "numeric values against the original data source. "
            "Do not remove records without confirmation."
        ),
        "affected_count": anomaly_count,
    }]

def generate_duplicate_recommendations(duplicate_results):
    """
    Generate recommendations for potential duplicate records.

    Args:
        duplicate_results: List of fuzzy duplicate dictionaries.

    Returns:
        List of structured recommendations.
    """

    if duplicate_results is None:
        return []

    if not isinstance(duplicate_results, list):
        raise TypeError("Duplicate results must be a list.")

    if not duplicate_results:
        return []

    for duplicate in duplicate_results:
        if not isinstance(duplicate, dict):
            raise TypeError(
                "Each duplicate result must be a dictionary."
            )

    return [{
        "category": "Duplicate",
        "priority": "Medium",
        "issue": "Potential duplicate records detected",
        "recommendation": (
            "Review the matching records and compare their "
            "details before merging or removing duplicates. "
            "Preserve valid distinct records."
        ),
        "affected_count": len(duplicate_results),
    }]

def generate_drift_recommendations(drift_results):
    """
    Generate recommendations for detected data drift.

    Args:
        drift_results: List of data drift result dictionaries.

    Returns:
        List of structured recommendations.
    """

    if drift_results is None:
        return []

    if not isinstance(drift_results, list):
        raise TypeError("Drift results must be a list.")

    recommendations = []

    for drift in drift_results:

        if not isinstance(drift, dict):
            raise TypeError(
                "Each drift result must be a dictionary."
            )

        if not drift.get("drift_detected", False):
            continue

        column = drift.get("column", "Unknown")
        method = drift.get("method", "Unknown")
        score = drift.get("drift_score", 0)

        priority = "High" if score >= 0.25 else "Medium"

        recommendations.append({
            "category": "Drift",
            "priority": priority,
            "issue": (
                f"Data drift detected in column '{column}' "
                f"using {method}"
            ),
            "recommendation": (
                "Investigate changes in the column's data "
                "distribution. Check whether the changes are "
                "expected and update data processing or model "
                "assumptions if necessary."
            ),
            "affected_count": 1,
        })

    return recommendations

def generate_quality_regression_recommendations(history_comparison):
    """
    Generate recommendations when historical quality metrics regress.

    Args:
        history_comparison: Output dictionary from
            compare_quality_history().

    Returns:
        List of structured recommendations.
    """

    if history_comparison is None:
        return []

    if not isinstance(history_comparison, dict):
        raise TypeError(
            "History comparison must be a dictionary."
        )

    comparison = history_comparison.get("comparison", {})

    if not isinstance(comparison, dict):
        raise TypeError(
            "History comparison must contain a comparison dictionary."
        )

    recommendations = []

    for metric, details in comparison.items():

        if not isinstance(details, dict):
            raise TypeError(
                "Each metric comparison must be a dictionary."
            )

        if details.get("status") != "regressed":
            continue

        if metric in ("quality_score", "completeness"):
            priority = "High"
        else:
            priority = "Medium"

        recommendations.append({
            "category": "Quality",
            "priority": priority,
            "issue": (
                f"Data quality regression in '{metric}'"
            ),
            "recommendation": (
                "Compare the latest dataset with the previous "
                "execution. Investigate the cause of the regression "
                "and correct the underlying data quality problem."
            ),
            "affected_count": 1,
        })

    return recommendations

def generate_recommendations(
    validation_issues=None,
    anomaly_results=None,
    duplicate_results=None,
    drift_results=None,
    history_comparison=None,
):
    """
    Generate and prioritize all data quality recommendations.

    Returns:
        Combined list of structured recommendations.
    """

    recommendations = []

    recommendations.extend(
        generate_validation_recommendations(
            validation_issues
        )
    )

    recommendations.extend(
        generate_anomaly_recommendations(
            anomaly_results
        )
    )

    recommendations.extend(
        generate_duplicate_recommendations(
            duplicate_results
        )
    )

    recommendations.extend(
        generate_drift_recommendations(
            drift_results
        )
    )

    recommendations.extend(
        generate_quality_regression_recommendations(
            history_comparison
        )
    )

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3,
    }

    recommendations.sort(
        key=lambda item: priority_order.get(
            item["priority"], 4
        )
    )

    return recommendations
