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