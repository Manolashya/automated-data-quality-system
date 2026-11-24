def generate_quality_alerts(report, thresholds):
    """
    Generate alerts when dataset quality metrics violate
    configured thresholds.

    Args:
        report: Dataset profiling report.
        thresholds: Validated quality threshold dictionary.

    Returns:
        A list of quality alert dictionaries.
    """

    alerts = []

    # 1. Check overall quality score
    quality_score = report.get("overall_quality_score")

    if quality_score is not None:
        if quality_score < thresholds["minimum_overall_score"]:
            alerts.append({
                "metric": "Overall Quality Score",
                "actual_value": quality_score,
                "threshold": thresholds["minimum_overall_score"],
                "severity": "Critical",
                "message": (
                    f"Quality score is {quality_score}%, "
                    f"below the minimum required score of "
                    f"{thresholds['minimum_overall_score']}%."
                ),
            })

    # 2. Calculate missing-value percentage
    rows = report.get("rows", 0)
    columns = report.get("column_count", 0)

    if rows <= 0 or columns <= 0:
        raise ValueError(
            "Report must contain positive row and column counts."
        )

    missing_values = report.get("missing_values", {})
    total_missing = sum(missing_values.values())

    total_cells = rows * columns

    missing_percentage = (
        total_missing / total_cells
    ) * 100

    if missing_percentage > thresholds["maximum_missing_percentage"]:
        alerts.append({
            "metric": "Missing Values",
            "actual_value": round(missing_percentage, 2),
            "threshold": thresholds["maximum_missing_percentage"],
            "severity": "Warning",
            "message": (
                f"Missing-value percentage is "
                f"{missing_percentage:.2f}%, exceeding the "
                f"maximum allowed percentage of "
                f"{thresholds['maximum_missing_percentage']}%."
            ),
        })

    # 3. Calculate duplicate-row percentage
    duplicate_rows = report.get("duplicate_rows", 0)

    duplicate_percentage = (
        duplicate_rows / rows
    ) * 100

    if duplicate_percentage > thresholds["maximum_duplicate_percentage"]:
        alerts.append({
            "metric": "Duplicate Rows",
            "actual_value": round(duplicate_percentage, 2),
            "threshold": thresholds["maximum_duplicate_percentage"],
            "severity": "Warning",
            "message": (
                f"Duplicate-row percentage is "
                f"{duplicate_percentage:.2f}%, exceeding the "
                f"maximum allowed percentage of "
                f"{thresholds['maximum_duplicate_percentage']}%."
            ),
        })

    return alerts