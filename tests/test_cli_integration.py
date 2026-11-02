
from pathlib import Path

import pandas as pd
import pytest

from src.pipeline.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DIRTY_DATASET = PROJECT_ROOT / "data" / "raw" / "dirty_customer_data.csv"
REFERENCE_DATASET = PROJECT_ROOT / "data" / "raw" / "customer_data.csv"


def test_cli_executes_pipeline_and_saves_output(
    monkeypatch,
    tmp_path,
    capsys
):
    """Test CLI execution and cleaned CSV output."""

    output_file = tmp_path / "cleaned_output.csv"

    monkeypatch.setattr(
        "sys.argv",
        [
            "cli.py",
            str(DIRTY_DATASET),
            "--output",
            str(output_file),
        ]
    )

    main()

    captured = capsys.readouterr()

    assert "PIPELINE EXECUTION COMPLETED" in captured.out
    assert "CLEANED DATASET SAVED SUCCESSFULLY" in captured.out

    assert output_file.exists()

    cleaned_df = pd.read_csv(output_file)

    assert cleaned_df.shape == (15, 10)
    assert not cleaned_df.duplicated().any()


def test_cli_with_reference_dataset(
    monkeypatch,
    tmp_path,
    capsys
):
    """Test CLI execution with optional reference dataset."""

    output_file = tmp_path / "drift_output.csv"

    monkeypatch.setattr(
        "sys.argv",
        [
            "cli.py",
            str(DIRTY_DATASET),
            "--reference",
            str(REFERENCE_DATASET),
            "--output",
            str(output_file),
        ]
    )

    main()

    captured = capsys.readouterr()

    assert "DATA DRIFT RESULTS" in captured.out
    assert "Data drift results: 10" in captured.out
    assert output_file.exists()


def test_cli_handles_missing_input_file(
    monkeypatch,
    capsys
):
    """Test CLI error handling for a missing input file."""

    missing_file = PROJECT_ROOT / "data" / "raw" / "missing.csv"

    monkeypatch.setattr(
        "sys.argv",
        ["cli.py", str(missing_file)]
    )

    with pytest.raises(SystemExit) as error:
        main()

    captured = capsys.readouterr()

    assert error.value.code == 1
    assert "ERROR: Input file not found" in captured.out


def test_cli_rejects_non_csv_input(
    monkeypatch,
    tmp_path,
    capsys
):
    """Test CLI rejection of files that are not CSV files."""

    text_file = tmp_path / "dataset.txt"
    text_file.write_text("This is not a CSV file.")

    monkeypatch.setattr(
        "sys.argv",
        ["cli.py", str(text_file)]
    )

    with pytest.raises(SystemExit) as error:
        main()

    captured = capsys.readouterr()

    assert error.value.code == 1
    assert "Input file must be a CSV file" in captured.out
