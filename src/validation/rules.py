
import pandas as pd

from src.utils.config_loader import load_config


def validate_dataframe(df):
    """
    Validate a pandas DataFrame using YAML-based configuration.

    Returns:
        A list of dictionaries describing validation issues.
    """

    # Load validation rules from YAML.
    config = load_config()

    required_columns = config["required_columns"]
    age_min = config["age"]["min"]
    age_max = config["age"]["max"]
    email_pattern = config["email"]["pattern"]

    valid_genders = {
        value.lower()
        for value in config["gender"]["allowed_values"]
    }

    numeric_rules = config["numeric_rules"]

    issues = []

    def add_issue(row_index, column, rule, value, message):
        issues.append({
            "row_index": row_index,
            "column": column,
            "rule": rule,
            "value": value,
            "message": message,
        })

    available_columns = set(df.columns)

    # Rule 1: Check required columns.
    for column in required_columns:
        if column not in available_columns:
            add_issue(
                None,
                column,
                "required_column",
                None,
                f"Required column '{column}' is missing.",
            )

    # Rule 2: Check missing values.
    if config.get("missing_values", {}).get(
        "check_required_columns", True
    ):
        for column in required_columns:
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

    # Rule 3: Age must be numeric and within configured limits.
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

        invalid_age = age.notna() & ~age.between(age_min, age_max)

        for row_index in df.index[invalid_age]:
            add_issue(
                row_index,
                "Age",
                "age_range",
                df.at[row_index, "Age"],
                f"Age must be between {age_min} and {age_max}.",
            )

    # Rule 4: Email must follow the configured pattern.
    if "Email" in available_columns:
        valid_email = df["Email"].astype("string").str.fullmatch(
            email_pattern,
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

    # Rule 5: Numeric columns must satisfy configured minimums.
    for rule_config in numeric_rules:
        column = rule_config["column"]

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

        minimum = rule_config.get("min")

        if minimum is not None:
            invalid_values = (
                numeric_values.notna()
                & (numeric_values < minimum)
            )

            for row_index in df.index[invalid_values]:
                add_issue(
                    row_index,
                    column,
                    "non_negative",
                    df.at[row_index, column],
                    f"{column} cannot be less than {minimum}.",
                )

    # Rule 6: Gender must be one of the configured values.
    if "Gender" in available_columns:
        gender = df["Gender"].astype("string").str.strip().str.lower()

        invalid_gender = (
            df["Gender"].notna()
            & ~gender.isin(valid_genders)
        )

        for row_index in df.index[invalid_gender]:
            add_issue(
                row_index,
                "Gender",
                "allowed_values",
                df.at[row_index, "Gender"],
                f"Gender must be one of: {', '.join(sorted(valid_genders))}.",
            )

    return issues
