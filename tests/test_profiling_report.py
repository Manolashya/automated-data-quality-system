
import json
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_SCRIPT = PROJECT_ROOT / "src" / "profiling" / "profile.py"
DATA_FILE = PROJECT_ROOT / "data" / "raw" / "customer_data.csv"
REPORT_FILE = PROJECT_ROOT / "reports" / "profiling_report.json"


@pytest.fixture(scope="module")
def profiling_report():
    """Run the profiling script and load its JSON report."""
    result = subprocess.run(
        [
            sys.executable,
            str(PROFILE_SCRIPT),
            str(DATA_FILE),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Profiling report saved successfully." in result.stdout
    assert REPORT_FILE.exists()

    with REPORT_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def test_profiling_report_has_expected_dataset_shape(profiling_report):
    assert profiling_report["dataset_shape"] == {
        "rows": 15,
        "columns": 10,
    }


def test_profiling_report_has_no_duplicate_rows(profiling_report):
    assert profiling_report["duplicate_rows"] == 0


def test_profiling_report_has_no_missing_values(profiling_report):
    missing_values = profiling_report["missing_values"]

    assert all(count == 0 for count in missing_values.values())


def test_profiling_report_has_expected_quality_score(profiling_report):
    assert profiling_report["overall_quality_score"] == 100.0


def test_profiling_report_detects_pii_columns(profiling_report):
    assert profiling_report["pii_columns"] == [
        "Customer_ID",
        "Name",
        "Email",
        "Phone",
    ]


def test_profiling_report_has_valid_validation_summary(profiling_report):
    summary = profiling_report["validation_summary"]

    assert len(summary) == 9
    assert all(score == 100.0 for score in summary.values())
