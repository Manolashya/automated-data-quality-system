
import pandas as pd
from pandas.testing import assert_frame_equal

from src.cleaning.cleaning_utils import impute_missing_values


def test_mean_imputation_for_numeric_column():
    df = pd.DataFrame({
        "Age": [20, None, 40],
    })

    result = impute_missing_values(df)

    assert result["Age"].tolist() == [20, 30, 40]


def test_median_imputation_for_outlier_column():
    df = pd.DataFrame({
        "Income": [10000, None, 20000, 100000],
    })

    result = impute_missing_values(
        df,
        median_columns=["Income"]
    )

    assert result["Income"].tolist() == [10000, 20000, 20000, 100000]


def test_mode_imputation_for_categorical_column():
    df = pd.DataFrame({
        "City": ["Bangalore", None, "Chennai", "Bangalore"],
    })

    result = impute_missing_values(df)

    assert result["City"].tolist() == [
        "Bangalore", "Bangalore", "Chennai", "Bangalore"
    ]


def test_entirely_missing_column_is_unchanged():
    df = pd.DataFrame({
        "Age": [None, None],
    })

    result = impute_missing_values(df)

    assert result["Age"].isna().all()


def test_original_dataframe_is_not_modified():
    df = pd.DataFrame({
        "Age": [20, None, 40],
        "City": ["Bangalore", None, "Chennai"],
    })

    original = df.copy(deep=True)

    impute_missing_values(df)

    assert_frame_equal(df, original)


def test_columns_without_missing_values_remain_unchanged():
    df = pd.DataFrame({
        "Age": [20, 30, 40],
        "City": ["Bangalore", "Chennai", "Hyderabad"],
    })

    result = impute_missing_values(df)

    assert_frame_equal(result, df)


def test_empty_dataframe():
    df = pd.DataFrame()

    result = impute_missing_values(df)

    assert_frame_equal(result, df)


def test_invalid_values_are_not_silently_converted():
    df = pd.DataFrame({
        "Age": ["20", None, "unknown"],
    })

    result = impute_missing_values(df)

    assert result["Age"].iloc[0] == "20"
    assert result["Age"].iloc[1] == "20"
    assert result["Age"].iloc[2] == "unknown"
