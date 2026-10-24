
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.duplicate_detection.detect import detect_fuzzy_duplicates


def test_detect_similar_names():
    df = pd.DataFrame({
        "Name": ["Rahul Kumar", "Rahul Kmar", "Priya Sharma"]
    })

    result = detect_fuzzy_duplicates(df, threshold=85)

    assert len(result) == 1
    assert result[0]["row_1"] == 0
    assert result[0]["row_2"] == 1
    assert result[0]["similarity"] >= 85


def test_ignore_missing_and_empty_names():
    df = pd.DataFrame({
        "Name": ["Rahul Kumar", None, "", "Priya Sharma"]
    })

    result = detect_fuzzy_duplicates(df)

    assert result == []


def test_case_insensitive_matching():
    df = pd.DataFrame({
        "Name": ["RAHUL KUMAR", "rahul kumar"]
    })

    result = detect_fuzzy_duplicates(df)

    assert len(result) == 1
    assert result[0]["similarity"] == 100


def test_threshold_filters_matches():
    df = pd.DataFrame({
        "Name": ["Rahul Kumar", "Rahul Kmar"]
    })

    result = detect_fuzzy_duplicates(df, threshold=99)

    assert result == []


def test_custom_column():
    df = pd.DataFrame({
        "City": ["Bangalore", "Bangalor"]
    })

    result = detect_fuzzy_duplicates(
        df,
        column="City",
        threshold=85
    )

    assert len(result) == 1
    assert result[0]["column"] == "City"


def test_missing_column_raises_error():
    df = pd.DataFrame({
        "Name": ["Rahul", "Rahil"]
    })

    with pytest.raises(ValueError):
        detect_fuzzy_duplicates(df, column="Email")


def test_invalid_threshold_raises_error():
    df = pd.DataFrame({
        "Name": ["Rahul", "Rahil"]
    })

    with pytest.raises(ValueError):
        detect_fuzzy_duplicates(df, threshold=110)


def test_original_dataframe_is_not_modified():
    df = pd.DataFrame({
        "Name": ["Rahul Kumar", "Rahul Kmar"]
    })

    original = df.copy(deep=True)

    detect_fuzzy_duplicates(df)

    assert_frame_equal(df, original)


def test_non_dataframe_input_raises_error():
    with pytest.raises(TypeError):
        detect_fuzzy_duplicates(["Rahul", "Rahil"])
