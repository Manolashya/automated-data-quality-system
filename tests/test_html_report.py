
import pytest

from src.reporting.html_report import generate_html_report


@pytest.fixture
def sample_profiling_report():
    """Provide a sample profiling report for testing."""

    return {
        "file_name": "test_dataset.csv",
        "rows": 3,
        "column_count": 2,
        "overall_quality_score": 100.0,
        "duplicate_rows": 0,
        "missing_values": {
            "Name": 0,
            "Age": 0,
        },
        "missing_percentage": {
            "Name": 0.0,
            "Age": 0.0,
        },
        "completeness_score": {
            "Name": 100.0,
            "Age": 100.0,
        },
        "validation_summary": {
            "email": 100.0,
            "age": 100.0,
        },
        "pii_columns": ["Name"],
    }


def test_html_report_is_generated(
    sample_profiling_report,
    tmp_path,
):
    output = tmp_path / "report.html"

    result = generate_html_report(
        sample_profiling_report,
        output_path=output,
    )

    assert result.exists()
    assert result == output
    assert result.stat().st_size > 0


def test_html_report_contains_dataset_information(
    sample_profiling_report,
    tmp_path,
):
    output = tmp_path / "report.html"

    generate_html_report(
        sample_profiling_report,
        output_path=output,
    )

    content = output.read_text(encoding="utf-8")

    assert "test_dataset.csv" in content
    assert "100.0%" in content
    assert "Total Rows" in content
    assert "Total Columns" in content


def test_html_report_contains_validation_issues(
    sample_profiling_report,
    tmp_path,
):
    output = tmp_path / "report.html"

    issues = [
        {
            "row_index": 2,
            "column": "Age",
            "rule": "age_range",
            "value": 150,
            "message": "Age must be between 0 and 120.",
        }
    ]

    generate_html_report(
        sample_profiling_report,
        issues,
        output,
    )

    content = output.read_text(encoding="utf-8")

    assert "age_range" in content
    assert "Age must be between 0 and 120." in content
    assert ">150<" in content


def test_html_report_handles_empty_validation_issues(
    sample_profiling_report,
    tmp_path,
):
    output = tmp_path / "report.html"

    generate_html_report(
        sample_profiling_report,
        output_path=output,
    )

    content = output.read_text(encoding="utf-8")

    assert "No validation issues found." in content


def test_html_report_escapes_html_content(
    sample_profiling_report,
    tmp_path,
):
    output = tmp_path / "report.html"

    issues = [
        {
            "row_index": 0,
            "column": "Name",
            "rule": "invalid_value",
            "value": "<script>alert(1)</script>",
            "message": "<script>alert(2)</script>",
        }
    ]

    generate_html_report(
        sample_profiling_report,
        issues,
        output,
    )

    content = output.read_text(encoding="utf-8")

    assert "<script>alert(1)</script>" not in content
    assert "<script>alert(2)</script>" not in content
    assert "&lt;script&gt;" in content


def test_invalid_profiling_report_raises_error():
    with pytest.raises(TypeError):
        generate_html_report("invalid report")


def test_empty_profiling_report_raises_error():
    with pytest.raises(ValueError):
        generate_html_report({})


def test_invalid_validation_issues_raise_error(
    sample_profiling_report,
):
    with pytest.raises(TypeError):
        generate_html_report(
            sample_profiling_report,
            validation_issues="invalid",
        )
