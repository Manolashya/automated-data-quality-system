
import pandas as pd
from pandas.testing import assert_frame_equal

from src.cleaning.cleaning_utils import (
    remove_exact_duplicates,
    normalize_text_and_gender,
    convert_numeric_columns,
)


def test_remove_exact_duplicates():
    """Check that exact duplicate rows are removed."""
    df = pd.DataFrame({
        "Name": ["Anu", "Ravi", "Anu"],
        "Age": [20, 21, 20],
    })

    result = remove_exact_duplicates(df)

    assert len(result) == 2
    assert not result.duplicated().any()


def test_normalize_text_and_gender():
    """Check whitespace removal and gender normalization."""
    df = pd.DataFrame({
        "Name": [" Anu ", " Ravi "],
        "Gender": ["F", "M"],
    })

    result = normalize_text_and_gender(df)

    assert result["Name"].tolist() == ["Anu", "Ravi"]
    assert result["Gender"].tolist() == ["Female", "Male"]


def test_convert_numeric_columns():
    """Check conversion of Age and Income to numeric values."""
    df = pd.DataFrame({
        "Age": ["25", "invalid"],
        "Income": ["50000", "60000"],
    })

    result = convert_numeric_columns(df)

    assert result["Age"].iloc[0] == 25
    assert pd.isna(result["Age"].iloc[1])
    assert result["Income"].tolist() == [50000, 60000]


def test_functions_do_not_modify_original_dataframe():
    """Check that the original DataFrame remains unchanged."""
    df = pd.DataFrame({
        "Name": [" Anu "],
        "Gender": ["F"],
        "Age": ["25"],
        "Income": ["50000"],
    })

    original = df.copy(deep=True)

    convert_numeric_columns(df)
    normalize_text_and_gender(df)
    remove_exact_duplicates(df)

    assert_frame_equal(df, original)
