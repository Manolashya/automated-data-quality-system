
import pandas as pd


REQUIRED_COLUMNS = [
    "Customer_ID",
    "Name",
    "Age",
    "Email",
    "Phone",
    "Gender",
    "City",
    "Income",
    "Purchase_Amount",
    "Purchase_Date",
]

VALID_GENDERS = {"male", "female"}

EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"


def validate_dataframe(df):
    """
    Validate a pandas DataFrame using predefined data quality rules.

    Returns:
        A list of dictionaries describing validation issues.
    """

    issues = []

    def add_issue(row_index, column, rule, value, message):
        issues.append({
            "row_index": row_index,
            "column": column,
            "rule": rule,
            "value": value,
            "message": message,
        })

    # Rule 1: Check whether required columns exist.
    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            add_issue(
                None,
                column,
                "required_column",
                None,
                f"Required column '{column}' is missing.",
            )

    # Stop checks for columns that do not exist.
    available_columns = set(df.columns)

    # Rule 2: Check missing values in required columns.
    for column in REQUIRED_COLUMNS:
        if column not in available_columns:
            continue

        missing_rows = df.index[df[column].isna()]

        for row_index in missing_rows:
            add_issue(
                row_index,
                column,
                "missing_value",
                None,
                f"Missing value in required column '{column}'.",
            )

    # Rule 3: Age must be numeric and between 0 and 120.
    if "Age" in available_columns:
        age = pd.to_numeric(df["Age"], errors="coerce")

        invalid_numeric = df["Age"].notna() & age.isna()

        for row_index in df.index[invalid_numeric]:
            add_issue(
                row_index,
                "Age",
                "numeric",
                df.at[row_index, "Age"],
                "Age must be a numeric value.",
            )

        invalid_age = age.notna() & ~age.between(0, 120)

        for row_index in df.index[invalid_age]:
            add_issue(
                row_index,
                "Age",
                "age_range",
                df.at[row_index, "Age"],
                "Age must be between 0 and 120.",
            )

    # Rule 4: Email must follow a valid email format.
    if "Email" in available_columns:
        valid_email = df["Email"].astype("string").str.fullmatch(
            EMAIL_PATTERN,
            case=False,
            na=False,
        )

        invalid_email = df["Email"].notna() & ~valid_email

        for row_index in df.index[invalid_email]:
            add_issue(
                row_index,
                "Email",
                "email_format",
                df.at[row_index, "Email"],
                "Invalid email format.",
            )

    # Rule 5: Income and Purchase_Amount must be numeric
    # and non-negative.
    for column in ["Income", "Purchase_Amount"]:
        if column not in available_columns:
            continue

        numeric_values = pd.to_numeric(df[column], errors="coerce")

        invalid_numeric = df[column].notna() & numeric_values.isna()

        for row_index in df.index[invalid_numeric]:
            add_issue(
                row_index,
                column,
                "numeric",
                df.at[row_index, column],
                f"{column} must be numeric.",
            )

        negative_values = numeric_values.notna() & (numeric_values < 0)

        for row_index in df.index[negative_values]:
            add_issue(
                row_index,
                column,
                "non_negative",
                df.at[row_index, column],
                f"{column} cannot be negative.",
            )

    # Rule 6: Gender must be Male or Female.
    if "Gender" in available_columns:
        gender = df["Gender"].astype("string").str.strip().str.lower()

        invalid_gender = (
            df["Gender"].notna()
            & ~gender.isin(VALID_GENDERS)
        )

        for row_index in df.index[invalid_gender]:
            add_issue(
                row_index,
                "Gender",
                "allowed_values",
                df.at[row_index, "Gender"],
                "Gender must be Male or Female.",
            )

    return issues
