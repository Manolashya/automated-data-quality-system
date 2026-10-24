import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.data_drift.detect import detect_data_drift


def test_detect_numerical_drift():
    reference = pd.DataFrame({
        "Income": [20000, 22000, 24000, 26000, 28000]
    })

    current = pd.DataFrame({
        "Income": [60000, 62000, 64000, 66000, 68000]
    })

    result = detect_data_drift(reference, current)

    assert len(result) == 1
    assert result[0]["method"] == "PSI"
    assert result[0]["drift_detected"] is True


def test_no_numerical_drift():
    reference = pd.DataFrame({
        "Income": [20000, 22000, 24000, 26000, 28000]
    })

    current = reference.copy()

    result = detect_data_drift(reference, current)

    assert result[0]["drift_score"] == 0.0
    assert result[0]["drift_detected"] is False


def test_detect_categorical_drift():
    reference = pd.DataFrame({
        "City": ["Bangalore", "Bangalore", "Chennai", "Chennai"]
    })

    current = pd.DataFrame({
        "City": ["Mumbai", "Mumbai", "Delhi", "Delhi"]
    })

    result = detect_data_drift(reference, current)

    assert result[0]["method"] == "TVD"
    assert result[0]["drift_detected"] is True
    assert result[0]["drift_score"] == 1.0


def test_no_categorical_drift():
    reference = pd.DataFrame({
        "City": ["Bangalore", "Chennai", "Bangalore", "Chennai"]
    })

    current = reference.copy()

    result = detect_data_drift(reference, current)

    assert result[0]["drift_score"] == 0.0
    assert result[0]["drift_detected"] is False


def test_ignore_columns_not_present_in_both_datasets():
    reference = pd.DataFrame({
        "Income": [20000, 22000],
        "Age": [20, 25]
    })

    current = pd.DataFrame({
        "Income": [60000, 62000],
        "City": ["Chennai", "Bangalore"]
    })

    result = detect_data_drift(reference, current)

    assert len(result) == 1
    assert result[0]["column"] == "Income"


def test_skip_columns_with_only_missing_values():
    reference = pd.DataFrame({
        "Income": [None, None]
    })

    current = pd.DataFrame({
        "Income": [None, None]
    })

    result = detect_data_drift(reference, current)

    assert result == []


def test_invalid_reference_input():
    with pytest.raises(TypeError):
        detect_data_drift(
            ["Bangalore", "Chennai"],
            pd.DataFrame({"City": ["Bangalore"]})
        )


def test_invalid_threshold():
    reference = pd.DataFrame({"Income": [10, 20, 30]})
    current = pd.DataFrame({"Income": [40, 50, 60]})

    with pytest.raises(ValueError):
        detect_data_drift(reference, current, threshold=-0.1)


def test_invalid_bins():
    reference = pd.DataFrame({"Income": [10, 20, 30]})
    current = pd.DataFrame({"Income": [40, 50, 60]})

    with pytest.raises(ValueError):
        detect_data_drift(reference, current, bins=1)


def test_original_dataframes_are_not_modified():
    reference = pd.DataFrame({
        "Income": [20000, 22000, 24000],
        "City": ["Bangalore", "Chennai", "Bangalore"]
    })

    current = pd.DataFrame({
        "Income": [60000, 62000, 64000],
        "City": ["Mumbai", "Delhi", "Mumbai"]
    })

    original_reference = reference.copy(deep=True)
    original_current = current.copy(deep=True)

    detect_data_drift(reference, current)

    assert_frame_equal(reference, original_reference)
    assert_frame_equal(current, original_current)