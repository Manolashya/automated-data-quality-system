import pandas as pd


def remove_exact_duplicates(df):
    """Remove rows that are exact duplicates."""
    return df.drop_duplicates().copy()


def normalize_text_and_gender(df):
    """Remove extra spaces and standardize gender values."""
    df = df.copy()

    text_columns = df.select_dtypes(include="str").columns

    for column in text_columns:
        df[column] = df[column].str.strip()

    if "Gender" in df.columns:
        df["Gender"] = df["Gender"].replace({
            "M": "Male",
            "F": "Female"
        })

    return df


def convert_numeric_columns(df):
    """Convert Age and Income to numeric values."""
    df = df.copy()

    for column in ["Age", "Income"]:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df

def impute_missing_values(df, median_columns=None):
    """
    Fill missing values using mean, median, or mode.

    Numerical columns use mean by default.
    Numerical columns listed in median_columns use median.
    Non-numerical columns use mode.
    Entirely missing columns are left unchanged.

    Returns a new DataFrame without modifying the original.
    """
    df = df.copy(deep=True)

    if median_columns is None:
        median_columns = []

    for column in df.columns:
        if not df[column].isna().any():
            continue

        # Leave columns with no available values unchanged.
        if df[column].isna().all():
            continue

        if pd.api.types.is_numeric_dtype(df[column]):
            if column in median_columns:
                fill_value = df[column].median()
            else:
                fill_value = df[column].mean()
        else:
            modes = df[column].mode(dropna=True)

            if modes.empty:
                continue

            fill_value = modes.iloc[0]

        df[column] = df[column].fillna(fill_value)

    return df
