
from pathlib import Path

import pandas as pd


OUTPUT_FILE = Path("data/processed/cleaned_data.csv")


def test_cleaned_dataset_exists():
    """Check that the cleaning pipeline created its output."""
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
