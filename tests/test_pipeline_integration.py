
from pathlib import Path

import pandas as pd
import pytest

from src.pipeline.runner import run_pipeline


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


def test_complete_pipeline_execution(dirty_df):
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
    }

    assert set(results.keys()) == expected_keys

    assert isinstance(results["cleaned_data"], pd.DataFrame)
    assert isinstance(results["validation_issues"], list)
    assert isinstance(results["anomaly_results"], pd.DataFrame)
    assert isinstance(results["duplicate_results"], list)
    assert isinstance(results["drift_results"], list)

    assert results["cleaned_data"].shape == (15, 10)
    assert results["drift_results"] == []

    assert isinstance(results["html_report_path"], Path)
    assert results["html_report_path"].exists()
    assert results["html_report_path"].suffix == ".html"


def test_pipeline_generates_html_report(dirty_df):
    """Test that the pipeline generates a complete HTML report."""

    results = run_pipeline(dirty_df)

    report_path = results["html_report_path"]
    report_content = report_path.read_text(encoding="utf-8")

    assert "<html" in report_content.lower()
    assert "pipeline_dataset.csv" in report_content
    assert "Data Quality Report" in report_content
    assert "Validation Issues" in report_content
    assert "Missing Values" in report_content


def test_pipeline_does_not_modify_original_dataset(dirty_df):
    """Test that pipeline execution preserves the original DataFrame."""

    original_df = dirty_df.copy(deep=True)

    run_pipeline(dirty_df)

    pd.testing.assert_frame_equal(dirty_df, original_df)


def test_cleaning_and_validation_integration(dirty_df):
    """Test that cleaning and validation work together."""

    results = run_pipeline(dirty_df)

    cleaned_df = results["cleaned_data"]
    validation_issues = results["validation_issues"]

    assert len(cleaned_df) == 15
    assert not cleaned_df.duplicated().any()
    assert isinstance(validation_issues, list)

    # Missing and invalid email values should be reported,
    # not automatically invented by the cleaning process.
    assert any(
        issue["column"] == "Email"
        for issue in validation_issues
    )


def test_anomaly_and_duplicate_detection_integration(dirty_df):
    """Test anomaly and fuzzy duplicate detection results."""

    results = run_pipeline(dirty_df)

    anomaly_results = results["anomaly_results"]
    duplicate_results = results["duplicate_results"]

    assert "Anomaly" in anomaly_results.columns
    assert "Anomaly_Score" in anomaly_results.columns

    assert isinstance(duplicate_results, list)


def test_pipeline_with_reference_dataset(dirty_df, reference_df):
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


def test_pipeline_rejects_non_dataframe():
    """Test that invalid input types raise TypeError."""

    with pytest.raises(TypeError, match="Input must be a pandas DataFrame"):
        run_pipeline([1, 2, 3])


def test_pipeline_rejects_empty_dataframe():
    """Test that an empty DataFrame raises ValueError."""

    with pytest.raises(ValueError, match="Input DataFrame cannot be empty"):
        run_pipeline(pd.DataFrame())
