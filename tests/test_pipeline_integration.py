
from pathlib import Path

import pandas as pd
import pytest

from src.pipeline.runner import run_pipeline
from src.history.history_comparator import compare_quality_history
from src.alerts.alert_history import load_alert_history
from src.history.history_tracker import DEFAULT_HISTORY_PATH
from src.history.risk_history import load_risk_history


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DIRTY_DATASET = PROJECT_ROOT / "data" / "raw" / "dirty_customer_data.csv"
REFERENCE_DATASET = PROJECT_ROOT / "data" / "raw" / "customer_data.csv"


@pytest.fixture
def dirty_df():
    """Load the dirty customer dataset."""
    return pd.read_csv(DIRTY_DATASET)


@pytest.fixture
def reference_df():
    """Load the clean reference dataset."""
    return pd.read_csv(REFERENCE_DATASET)


@pytest.fixture
def temporary_history(monkeypatch, tmp_path):
    """Use temporary files for quality and alert history."""

    history_path = tmp_path / "quality_history.csv"
    alert_history_path = tmp_path / "quality_alert_history.csv"
    risk_history_path = tmp_path / "risk_history.csv"

    monkeypatch.setattr(
        "src.history.history_tracker.DEFAULT_HISTORY_PATH",
        history_path
    )

    monkeypatch.setattr(
        "src.alerts.alert_history.DEFAULT_ALERT_HISTORY_PATH",
        alert_history_path
    )
    monkeypatch.setattr(
        "src.history.risk_history.DEFAULT_RISK_HISTORY_PATH",
        risk_history_path
    )

    mitigation_path = tmp_path / "mitigation_actions.csv"

    monkeypatch.setattr(
        "src.history.mitigation_tracker.DEFAULT_MITIGATION_PATH",
        mitigation_path
    )

    return history_path


def test_complete_pipeline_execution(dirty_df, temporary_history):
    """Test that all pipeline stages execute and return results."""

    results = run_pipeline(dirty_df)

    expected_keys = {
        "cleaned_data",
        "validation_issues",
        "profiling_report",
        "anomaly_results",
        "duplicate_results",
        "drift_results",
        "html_report_path",
        "history_path",
        "recommendations",
        "alerts",
        "alert_history_path",
        "risk_result",
        "risk_history_path",
        "mitigation_actions",
        "mitigation_actions_path",
    }

    assert set(results.keys()) == expected_keys

    assert isinstance(results["cleaned_data"], pd.DataFrame)
    assert isinstance(results["validation_issues"], list)
    assert isinstance(results["anomaly_results"], pd.DataFrame)
    assert isinstance(results["duplicate_results"], list)
    assert isinstance(results["drift_results"], list)
    assert isinstance(results["recommendations"], list)
    assert isinstance(results["alerts"], list)
    assert isinstance(results["mitigation_actions"], pd.DataFrame)
    assert isinstance(results["mitigation_actions_path"], Path)
    assert results["mitigation_actions_path"].exists()
    assert results["mitigation_actions_path"].name == "mitigation_actions.csv"

    assert results["cleaned_data"].shape == (15, 10)
    assert results["drift_results"] == []

    assert isinstance(results["html_report_path"], Path)
    assert results["html_report_path"].exists()
    assert results["html_report_path"].suffix == ".html"

    assert isinstance(results["history_path"], Path)
    assert results["history_path"].exists()
    assert results["history_path"] == temporary_history

    assert isinstance(results["alert_history_path"], Path)
    # Alert history is created only when at least one alert exists.
    assert (
        results["alert_history_path"].exists()
        == bool(results["alerts"])
        )
    assert results["alert_history_path"].name == "quality_alert_history.csv"


def test_pipeline_generates_html_report(dirty_df, temporary_history):
    """Test that the pipeline generates a complete HTML report."""

    results = run_pipeline(dirty_df)

    report_path = results["html_report_path"]
    report_content = report_path.read_text(encoding="utf-8")

    assert "<html" in report_content.lower()
    assert "pipeline_dataset.csv" in report_content
    assert "Data Quality Report" in report_content
    assert "Validation Issues" in report_content
    assert "Missing Values" in report_content


def test_pipeline_does_not_modify_original_dataset(
    dirty_df,
    temporary_history
):
    """Test that pipeline execution preserves the original DataFrame."""

    original_df = dirty_df.copy(deep=True)

    run_pipeline(dirty_df)

    pd.testing.assert_frame_equal(dirty_df, original_df)


def test_cleaning_and_validation_integration(dirty_df, temporary_history):
    """Test that cleaning and validation work together."""

    results = run_pipeline(dirty_df)

    cleaned_df = results["cleaned_data"]
    validation_issues = results["validation_issues"]

    assert len(cleaned_df) == 15
    assert not cleaned_df.duplicated().any()
    assert isinstance(validation_issues, list)

    assert any(
        issue["column"] == "Email"
        for issue in validation_issues
    )


def test_anomaly_and_duplicate_detection_integration(
    dirty_df,
    temporary_history
):
    """Test anomaly and fuzzy duplicate detection results."""

    results = run_pipeline(dirty_df)

    anomaly_results = results["anomaly_results"]
    duplicate_results = results["duplicate_results"]

    assert "Anomaly" in anomaly_results.columns
    assert "Anomaly_Score" in anomaly_results.columns

    assert isinstance(duplicate_results, list)


def test_pipeline_with_reference_dataset(
    dirty_df,
    reference_df,
    temporary_history
):
    """Test pipeline execution with optional drift detection."""

    results = run_pipeline(
        dirty_df,
        reference_df=reference_df
    )

    drift_results = results["drift_results"]

    assert isinstance(drift_results, list)
    assert len(drift_results) > 0

    for drift in drift_results:
        assert "column" in drift
        assert "method" in drift
        assert "drift_score" in drift
        assert "drift_detected" in drift


def test_pipeline_rejects_non_dataframe(temporary_history):
    """Test that invalid input types raise TypeError."""

    with pytest.raises(TypeError, match="Input must be a pandas DataFrame"):
        run_pipeline([1, 2, 3])


def test_pipeline_rejects_empty_dataframe(temporary_history):
    """Test that an empty DataFrame raises ValueError."""

    with pytest.raises(ValueError, match="Input DataFrame cannot be empty"):
        run_pipeline(pd.DataFrame())


def test_pipeline_appends_history_records(dirty_df, temporary_history):
    """Test that repeated pipeline executions create separate records."""

    run_pipeline(dirty_df)
    run_pipeline(dirty_df)

    history = pd.read_csv(temporary_history)

    assert len(history) == 2
    assert list(history.columns) == [
        "timestamp",
        "dataset_name",
        "rows",
        "columns",
        "quality_score",
        "completeness",
        "missing_values",
        "duplicate_rows",
        "validation_issues",
        "anomalies",
    ]

    assert all(
        history["dataset_name"] == "pipeline_dataset.csv"
    )


# ============================================================
# Day 50: Extended End-to-End Integration Tests
# ============================================================

from src.alerts.quality_alerts import generate_quality_alerts
from src.utils.config_loader import load_config
from src.utils.threshold_validator import validate_quality_thresholds
import src.pipeline.runner as pipeline_runner


def test_profiling_report_integrates_with_quality_alerts(
    dirty_df,
    temporary_history
):
    """Test that pipeline profiling results work with the alert engine."""

    results = run_pipeline(dirty_df)

    report = results["profiling_report"]

    threshold_config = load_config(
        PROJECT_ROOT / "config" / "quality_thresholds.yaml"
    )

    thresholds = validate_quality_thresholds(threshold_config)

    alerts = generate_quality_alerts(report, thresholds)

    assert isinstance(report, dict)
    assert "overall_quality_score" in report
    assert "missing_values" in report
    assert "duplicate_rows" in report

    assert isinstance(alerts, list)

    for alert in alerts:
        assert {
            "metric",
            "actual_value",
            "threshold",
            "severity",
            "message",
        }.issubset(alert.keys())


def test_pipeline_recommendations_have_valid_structure(
    dirty_df,
    temporary_history
):
    """Test the structure of recommendations from a real pipeline run."""

    results = run_pipeline(dirty_df)

    recommendations = results["recommendations"]

    assert isinstance(recommendations, list)

    for recommendation in recommendations:
        assert {
            "category",
            "priority",
            "issue",
            "recommendation",
            "affected_count",
        }.issubset(recommendation.keys())

        assert recommendation["priority"] in [
            "High",
            "Medium",
            "Low",
        ]

        assert isinstance(
            recommendation["affected_count"],
            int
        )


def test_pipeline_history_comparison_integration(
    dirty_df,
    temporary_history
):
    """Test that repeated pipeline runs produce comparable history."""

    run_pipeline(dirty_df)
    run_pipeline(dirty_df)

    comparison = compare_quality_history(temporary_history)

    assert isinstance(comparison, dict)

    assert "previous_execution" in comparison
    assert "latest_execution" in comparison
    assert "comparison" in comparison

    assert isinstance(comparison["comparison"], dict)

    assert {
        "quality_score",
        "completeness",
        "missing_values",
        "duplicate_rows",
        "validation_issues",
        "anomalies",
    }.issubset(comparison["comparison"].keys())


def test_pipeline_propagates_internal_errors(
    dirty_df,
    temporary_history,
    monkeypatch
):
    """Test that unexpected pipeline errors are propagated."""

    def raise_cleaning_error(df):
        raise RuntimeError("Simulated cleaning failure")

    monkeypatch.setattr(
        pipeline_runner,
        "clean_dataframe",
        raise_cleaning_error
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated cleaning failure"
    ):
        run_pipeline(dirty_df)


# ============================================================
# Day 51: Alert History Integration Tests
# ============================================================

def test_pipeline_persists_generated_alerts(
    dirty_df,
    temporary_history
):
    """Test that pipeline alerts are saved with the dataset name."""

    results = run_pipeline(
        dirty_df,
        dataset_name="dirty_customer_data.csv"
    )

    saved_alerts = load_alert_history(
        results["alert_history_path"]
    )

    assert isinstance(results["alerts"], list)
    assert len(saved_alerts) == len(results["alerts"])

    for alert in saved_alerts:
        assert alert["dataset_name"] == "dirty_customer_data.csv"
        assert alert["timestamp"]
        assert alert["metric"]
        assert alert["severity"]


def test_pipeline_appends_alert_history_on_repeated_runs(
    dirty_df,
    temporary_history,
    monkeypatch
):
    """Test that repeated pipeline runs append separate alert records."""

    test_alert = {
        "metric": "quality_score",
        "actual_value": 70,
        "threshold": 80,
        "severity": "critical",
        "message": "Quality score is below the configured threshold.",
    }

    # Ensure every pipeline execution generates one predictable alert.
    monkeypatch.setattr(
        pipeline_runner,
        "generate_quality_alerts",
        lambda profiling_report, thresholds: [test_alert]
    )

    first_results = run_pipeline(
        dirty_df,
        dataset_name="first_run.csv"
    )

    second_results = run_pipeline(
        dirty_df,
        dataset_name="second_run.csv"
    )

    saved_alerts = load_alert_history(
        first_results["alert_history_path"]
    )

    assert len(first_results["alerts"]) == 1
    assert len(second_results["alerts"]) == 1
    assert len(saved_alerts) == 2

    dataset_names = {
        alert["dataset_name"]
        for alert in saved_alerts
    }

    assert dataset_names == {
        "first_run.csv",
        "second_run.csv",
    }

    for alert in saved_alerts:
        assert alert["timestamp"]
        assert alert["metric"] == "quality_score"
        assert alert["severity"] == "critical"
    """Test that repeated pipeline runs append separate alert records."""

    first_results = run_pipeline(
        dirty_df,
        dataset_name="first_run.csv"
    )

    run_pipeline(
        dirty_df,
        dataset_name="second_run.csv"
    )

    saved_alerts = load_alert_history(
        first_results["alert_history_path"]
    )

    assert len(saved_alerts) >= 2

    dataset_names = {
        alert["dataset_name"]
        for alert in saved_alerts
    }

    assert "first_run.csv" in dataset_names
    assert "second_run.csv" in dataset_names



# ============================================================
# Day 56: Risk History Pipeline Integration Tests
# ============================================================

def test_pipeline_persists_risk_assessment(
    dirty_df,
    temporary_history
):
    """Test that one successful pipeline run saves one risk record."""

    results = run_pipeline(dirty_df)

    risk_history = load_risk_history(
        results["risk_history_path"]
    )

    assert results["risk_history_path"].exists()
    assert len(risk_history) == 1

    assert results["risk_result"]["risk_score"] >= 0
    assert results["risk_result"]["risk_level"] in [
        "Low",
        "Medium",
        "High",
        "Critical",
    ]

    assert risk_history.iloc[0]["dataset_name"] == (
        results["profiling_report"]["file_name"]
    )

    assert float(risk_history.iloc[0]["risk_score"]) == (
        results["risk_result"]["risk_score"]
    )


def test_pipeline_appends_risk_history_on_repeated_runs(
    dirty_df,
    temporary_history
):
    """Test that each successful run appends exactly one risk record."""

    first_results = run_pipeline(dirty_df)
    second_results = run_pipeline(dirty_df)

    risk_history = load_risk_history(
        first_results["risk_history_path"]
    )

    assert len(risk_history) == 2
    assert first_results["risk_history_path"] == (
        second_results["risk_history_path"]
    )

    assert all(
        risk_history["dataset_name"]
        == first_results["profiling_report"]["file_name"]
    )


# ============================================================
# DAY 58: RISK MITIGATION ACTION TRACKING
# ============================================================

def test_pipeline_generates_mitigation_actions(
    dirty_df,
    temporary_history
):
    """Test that pipeline risk recommendations create saved tasks."""

    from src.history.mitigation_tracker import load_mitigation_actions

    results = run_pipeline(dirty_df)

    actions = load_mitigation_actions(
        results["mitigation_actions_path"]
    )

    assert not actions.empty
    assert len(actions) >= len(results["mitigation_actions"])
    assert set(actions["status"]) == {"Pending"}
    assert set(actions["dataset_name"]) == {
        results["risk_result"]["dataset_name"]
    }
    assert set(actions["risk_level"]) == {
        results["risk_result"]["risk_level"]
    }


def test_pipeline_does_not_duplicate_open_mitigation_actions(
    dirty_df,
    temporary_history
):
    """Test that repeated runs do not duplicate open mitigation tasks."""

    from src.history.mitigation_tracker import load_mitigation_actions

    first_results = run_pipeline(dirty_df)
    second_results = run_pipeline(dirty_df)

    first_actions = first_results["mitigation_actions"]
    second_actions = second_results["mitigation_actions"]

    saved_actions = load_mitigation_actions(
        second_results["mitigation_actions_path"]
    )

    assert not first_actions.empty

    # New recommendations may appear when quality history changes.
    # However, the same dataset/recommendation pair must not be duplicated.
    assert len(saved_actions) == (
        len(first_actions) + len(second_actions)
    )

    assert not saved_actions.duplicated(
        subset=["dataset_name", "recommendation"]
    ).any()

    assert not saved_actions["action_id"].duplicated().any()

    first_recommendations = set(first_actions["recommendation"])
    second_recommendations = set(second_actions["recommendation"])

    assert first_recommendations.isdisjoint(second_recommendations)
