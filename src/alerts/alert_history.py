
import csv
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_ALERT_HISTORY_PATH = (
    PROJECT_ROOT / "reports" / "quality_alert_history.csv"
)

ALERT_HISTORY_FIELDS = [
    "timestamp",
    "dataset_name",
    "metric",
    "actual_value",
    "threshold",
    "severity",
    "message",
]


def save_alert_history(alerts, dataset_name, history_path=None):
    """
    Append generated quality alerts to a CSV history file.

    Args:
        alerts: List of generated alert dictionaries.
        dataset_name: Name of the dataset that triggered the alerts.
        history_path: Optional custom CSV file path.

    Returns:
        Path to the alert history CSV file.
    """

    if not isinstance(alerts, list):
        raise TypeError("alerts must be a list.")

    if not isinstance(dataset_name, str) or not dataset_name.strip():
        raise ValueError("dataset_name must be a non-empty string.")

    required_fields = ALERT_HISTORY_FIELDS[2:]

    for alert in alerts:
        if not isinstance(alert, dict):
            raise TypeError("Every alert must be a dictionary.")

        for field in required_fields:
            if field not in alert:
                raise ValueError(
                    f"Missing required alert field: {field}"
                )

    output_path = (
        Path(history_path)
        if history_path is not None
        else DEFAULT_ALERT_HISTORY_PATH
    )

    # Return without creating a file when there are no alerts.
    if not alerts:
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)

    write_header = (
        not output_path.exists()
        or output_path.stat().st_size == 0
    )

    timestamp = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    with output_path.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=ALERT_HISTORY_FIELDS
        )

        if write_header:
            writer.writeheader()

        for alert in alerts:
            record = {
                "timestamp": timestamp,
                "dataset_name": dataset_name,
                **{
                    field: alert[field]
                    for field in required_fields
                },
            }

            writer.writerow(record)

    return output_path


def load_alert_history(history_path=None):
    """
    Load previously saved quality alerts from a CSV file.

    Returns:
        A list of alert dictionaries.
        Returns an empty list when the file does not exist
        or contains no records.
    """

    input_path = (
        Path(history_path)
        if history_path is not None
        else DEFAULT_ALERT_HISTORY_PATH
    )

    if not input_path.exists() or input_path.stat().st_size == 0:
        return []

    with input_path.open(
        "r",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        reader = csv.DictReader(csv_file)
        return list(reader)
