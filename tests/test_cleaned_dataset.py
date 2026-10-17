
from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "cleaned_data.csv"
CLEANING_SCRIPT = PROJECT_ROOT / "src" / "cleaning" / "clean.py"


@pytest.fixture(scope="module", autouse=True)
def run_cleaning_pipeline():
    """Run the actual cleaning script before integration tests."""
    result = subprocess.run(
        [sys.executable, str(CLEANING_SCRIPT)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Cleaned dataset saved successfully." in result.stdout
    assert OUTPUT_FILE.exists()
    return result.stdout


def test_cleaned_dataset_exists():
    """Check that the pipeline created its output."""
    assert OUTPUT_FILE.exists()


def test_cleaned_dataset_has_expected_shape():
    """Check the number of rows and columns."""
    df = pd.read_csv(OUTPUT_FILE)

    assert df.shape == (15, 10)


def test_cleaned_dataset_has_no_duplicate_rows():
    """Check that exact duplicate rows were removed."""
    df = pd.read_csv(OUTPUT_FILE)

    assert not df.duplicated().any()


def test_age_and_income_have_no_missing_values():
    """Check that Age and Income are completely filled."""
    df = pd.read_csv(OUTPUT_FILE)

    assert df["Age"].notna().all()
    assert df["Income"].notna().all()


def test_age_and_income_are_valid():
    """Check the allowed ranges for Age and Income."""
    df = pd.read_csv(OUTPUT_FILE)

    assert df["Age"].between(0, 100).all()
    assert (df["Income"] >= 0).all()


def test_gender_values_are_standardized():
    """Check that gender values use Male or Female."""
    df = pd.read_csv(OUTPUT_FILE)

    assert df["Gender"].isin(["Male", "Female"]).all()

def test_email_validation_detects_known_issues(run_cleaning_pipeline):
    """Check that known email issues are detected."""
    assert "Email validation completed" in run_cleaning_pipeline
    assert "Invalid emails detected: 1" in run_cleaning_pipeline
    assert "Missing emails detected: 1" in run_cleaning_pipeline


def test_phone_validation_detects_known_issues(run_cleaning_pipeline):
    """Check that the known invalid phone number is detected."""
    assert "Phone validation completed" in run_cleaning_pipeline
    assert "Invalid phone numbers detected: 1" in run_cleaning_pipeline


def test_purchase_date_validation_detects_known_issues(
    run_cleaning_pipeline,
):
    """Check that the known invalid purchase date is detected."""
    assert "Purchase date validation completed" in run_cleaning_pipeline
    assert "Invalid purchase dates detected: 1" in run_cleaning_pipeline
