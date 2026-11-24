
from src.alerts.alert_analytics import analyze_alert_history


RECOMMENDATIONS = {
    "Overall Quality Score": (
        "Review the quality report to identify the underlying issues. "
        "Fix the highest-impact validation and cleaning problems first."
    ),
    "Missing Values": (
        "Inspect columns containing missing values. Apply suitable "
        "imputation or correction rules and verify required fields."
    ),
    "Duplicate Rows": (
        "Inspect duplicate records and define a reliable uniqueness "
        "rule before removing duplicate entries."
    ),
    "Unknown": (
        "Inspect the alert record and verify its metric, dataset, "
        "severity, and timestamp fields."
    ),
}


def generate_alert_insights(alert_history):
    """
    Generate actionable insights from historical quality alerts.

    Returns a list of insight dictionaries containing:
    priority, title, finding, and recommendation.
    """

    analytics = analyze_alert_history(alert_history)

    insights = []

    if analytics["total_alerts"] == 0:
        return insights

    severity_counts = analytics["severity_counts"]
    metric_counts = analytics["metric_counts"]
    dataset_counts = analytics["dataset_counts"]

    # Critical alert insight.
    critical_count = severity_counts.get("Critical", 0)

    if critical_count:
        insights.append({
            "priority": "High",
            "title": "Critical quality alerts detected",
            "finding": (
                f"{critical_count} critical alert(s) were recorded."
            ),
            "recommendation": (
                "Investigate critical quality issues first and "
                "rerun validation after applying corrections."
            ),
        })

    # Most frequently affected metric.
    if metric_counts:
        metric, count = next(iter(metric_counts.items()))

        insights.append({
            "priority": "High" if count >= 3 else "Medium",
            "title": "Most frequently affected metric",
            "finding": (
                f"{metric} generated {count} alert(s)."
            ),
            "recommendation": RECOMMENDATIONS.get(
                metric,
                "Investigate this metric and review its validation rules."
            ),
        })

    # Dataset with the most alerts.
    if dataset_counts:
        dataset, count = next(iter(dataset_counts.items()))

        if count >= 2:
            insights.append({
                "priority": "Medium",
                "title": "Repeated alerts for one dataset",
                "finding": (
                    f"{dataset} generated {count} historical alert(s)."
                ),
                "recommendation": (
                    "Review this dataset's recent quality reports, "
                    "identify recurring problems, and correct their "
                    "root causes."
                ),
            })

    return insights
