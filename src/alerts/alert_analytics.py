
from collections import Counter
from datetime import datetime


def analyze_alert_history(alert_history):
    """
    Analyze historical quality alerts.

    Args:
        alert_history: List of alert dictionaries loaded
                       from the alert history CSV file.

    Returns:
        A dictionary containing alert analytics:
        - total_alerts
        - severity_counts
        - metric_counts
        - dataset_counts
        - daily_counts
    """

    if not isinstance(alert_history, list):
        raise TypeError("alert_history must be a list.")

    severity_counter = Counter()
    metric_counter = Counter()
    dataset_counter = Counter()
    daily_counter = Counter()

    for alert in alert_history:

        if not isinstance(alert, dict):
            raise TypeError(
                "Every alert history record must be a dictionary."
            )

        # Count alerts by severity.
        severity = alert.get("severity") or "Unknown"
        severity_counter[severity] += 1

        # Count alerts by metric.
        metric = alert.get("metric") or "Unknown"
        metric_counter[metric] += 1

        # Count alerts by dataset.
        dataset = alert.get("dataset_name") or "Unknown"
        dataset_counter[dataset] += 1

        # Group alerts by date.
        timestamp = alert.get("timestamp", "")

        try:
            alert_date = datetime.fromisoformat(
                timestamp
            ).date().isoformat()

        except (ValueError, TypeError):
            alert_date = "Unknown"

        daily_counter[alert_date] += 1

    # Sort counts from highest to lowest.
    # Alphabetical order breaks ties for predictable results.
    def sort_counts(counter):
        return dict(
            sorted(
                counter.items(),
                key=lambda item: (-item[1], item[0])
            )
        )

    # Keep daily trends in chronological order.
    daily_counts = dict(
        sorted(
            daily_counter.items(),
            key=lambda item: (
                item[0] == "Unknown",
                item[0]
            )
        )
    )

    return {
        "total_alerts": len(alert_history),
        "severity_counts": sort_counts(severity_counter),
        "metric_counts": sort_counts(metric_counter),
        "dataset_counts": sort_counts(dataset_counter),
        "daily_counts": daily_counts,
    }
