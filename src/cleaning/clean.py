
import pandas as pd
from pathlib import Path

try:
    from .cleaning_utils import (
        remove_exact_duplicates,
        normalize_text_and_gender,
        convert_numeric_columns,
    )
except ImportError:
    # Support running this file directly from the terminal.
    from cleaning_utils import (
        remove_exact_duplicates,
        normalize_text_and_gender,
        convert_numeric_columns,
    )


def clean_dataframe(df, verbose=False):
    """
    Clean a DataFrame without modifying the original.

    Returns:
        pandas.DataFrame: Cleaned dataset.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Input DataFrame cannot be empty.")

    df = df.copy(deep=True)

    def log(message):
        if verbose:
            print(message)

    df = convert_numeric_columns(df)

    log("DATASET LOADED")
    log("-" * 40)
    log(f"Original Shape: {df.shape}")

    # Detect repeated Customer_ID values.
    if "Customer_ID" in df.columns:
        customer_ids = df["Customer_ID"].astype("string").str.strip()

        duplicate_mask = (
            customer_ids.notna()
            & customer_ids.duplicated(keep=False)
        )

        duplicate_ids = sorted(
            customer_ids[duplicate_mask].unique().tolist()
        )

        log(
            "Rows with repeated Customer_ID: "
            f"{int(duplicate_mask.sum())}"
        )
        log(f"Repeated Customer_ID values: {duplicate_ids}")

    # Remove exact duplicates.
    df = remove_exact_duplicates(df)
    log(f"After Duplicate Removal: {df.shape}")

    # Normalize text and gender.
    df = normalize_text_and_gender(df)

    log("Whitespace cleaned")
    log("Gender values normalized")

    # Handle invalid Age values.
    invalid_age_count = 0

    if "Age" in df.columns:
        invalid_ages = (
            df["Age"].notna()
            & ~df["Age"].between(0, 100)
        )

        invalid_age_count = int(invalid_ages.sum())
        df.loc[invalid_ages, "Age"] = float("nan")

        log("Invalid Age values handled")

    # Handle invalid Income values.
    invalid_income_count = 0

    if "Income" in df.columns:
        invalid_incomes = (
            df["Income"].notna()
            & (df["Income"] < 0)
        )

        invalid_income_count = int(invalid_incomes.sum())
        df.loc[invalid_incomes, "Income"] = float("nan")

        log("Invalid Income values handled")

    # Fill missing Age values using the median.
    missing_age_count = 0

    if "Age" in df.columns:
        missing_age_count = int(df["Age"].isna().sum())
        age_median = df["Age"].median()

        if pd.notna(age_median):
            df["Age"] = df["Age"].fillna(age_median)
            log("Missing Age values filled using median")
        elif missing_age_count > 0:
            log(
                "Warning: Age contains only missing values; "
                "median imputation is not possible"
            )

    # Fill missing Income values using the median.
    missing_income_count = 0

    if "Income" in df.columns:
        missing_income_count = int(df["Income"].isna().sum())
        income_median = df["Income"].median()

        if pd.notna(income_median):
            df["Income"] = df["Income"].fillna(income_median)
            log("Missing Income values filled using median")
        elif missing_income_count > 0:
            log(
                "Warning: Income contains only missing values; "
                "median imputation is not possible"
            )

    # Email validation.
    invalid_email_count = 0
    missing_email_count = 0

    if "Email" in df.columns:
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        email_values = df["Email"].astype("string")

        missing_email_count = int(email_values.isna().sum())

        valid_mask = email_values.str.match(
            email_pattern,
            na=False
        )

        invalid_email_count = int(
            (~valid_mask & email_values.notna()).sum()
        )

        log("Email validation completed")

    # Phone validation.
    invalid_phone_count = 0
    missing_phone_count = 0

    if "Phone" in df.columns:
        phone_values = df["Phone"].astype("string").str.strip()

        missing_phone_count = int(phone_values.isna().sum())

        valid_mask = phone_values.str.match(
            r"^[6-9]\d{9}$",
            na=False
        )

        invalid_phone_count = int(
            (~valid_mask & phone_values.notna()).sum()
        )

        log("Phone validation completed")

    # Purchase date validation.
    invalid_date_count = 0
    missing_date_count = 0

    if "Purchase_Date" in df.columns:
        date_values = (
            df["Purchase_Date"].astype("string").str.strip()
        )

        missing_date_count = int(date_values.isna().sum())

        parsed_dates = pd.to_datetime(
            date_values,
            format="%Y-%m-%d",
            errors="coerce"
        )

        invalid_date_count = int(
            (parsed_dates.isna() & date_values.notna()).sum()
        )

        log("Purchase date validation completed")

    # Purchase amount validation.
    invalid_purchase_amount_count = 0
    missing_purchase_amount_count = 0

    if "Purchase_Amount" in df.columns:
        amount_values = pd.to_numeric(
            df["Purchase_Amount"],
            errors="coerce"
        )

        missing_purchase_amount_count = int(
            df["Purchase_Amount"].isna().sum()
            + (
                df["Purchase_Amount"].notna()
                & amount_values.isna()
            ).sum()
        )

        invalid_purchase_amount_count = int(
            (amount_values < 0).sum()
        )

        log("Purchase amount validation completed")

    # Customer ID validation.
    invalid_customer_id_count = 0
    missing_customer_id_count = 0

    if "Customer_ID" in df.columns:
        customer_ids = (
            df["Customer_ID"].astype("string").str.strip()
        )

        missing_customer_id_count = int(customer_ids.isna().sum())

        valid_mask = customer_ids.str.match(
            r"^C\d{3}$",
            na=False
        )

        invalid_customer_id_count = int(
            (~valid_mask & customer_ids.notna()).sum()
        )

        log("Customer ID validation completed")

    # Gender validation.
    invalid_gender_count = 0
    missing_gender_count = 0

    if "Gender" in df.columns:
        gender_values = (
            df["Gender"].astype("string").str.strip()
        )

        missing_gender_count = int(gender_values.isna().sum())

        valid_mask = gender_values.isin(["Male", "Female"])

        invalid_gender_count = int(
            (~valid_mask & gender_values.notna()).sum()
        )

        log("Gender validation completed")

    # City validation.
    invalid_city_count = 0
    missing_city_count = 0

    if "City" in df.columns:
        city_values = df["City"].astype("string").str.strip()

        missing_city_count = int(city_values.isna().sum())

        valid_mask = city_values.isin([
            "Hyderabad",
            "Bangalore",
            "Chennai"
        ])

        invalid_city_count = int(
            (~valid_mask & city_values.notna()).sum()
        )

        log("City validation completed")

    # Collect cleaning statistics.
    summary = {
        "invalid_age": invalid_age_count,
        "invalid_income": invalid_income_count,
        "missing_age_filled": missing_age_count,
        "missing_income_filled": missing_income_count,
        "invalid_email": invalid_email_count,
        "missing_email": missing_email_count,
        "invalid_phone": invalid_phone_count,
        "missing_phone": missing_phone_count,
        "invalid_purchase_date": invalid_date_count,
        "missing_purchase_date": missing_date_count,
        "invalid_purchase_amount": invalid_purchase_amount_count,
        "missing_purchase_amount": missing_purchase_amount_count,
        "invalid_customer_id": invalid_customer_id_count,
        "missing_customer_id": missing_customer_id_count,
        "invalid_gender": invalid_gender_count,
        "missing_gender": missing_gender_count,
        "invalid_city": invalid_city_count,
        "missing_city": missing_city_count,
    }

    if verbose:
        print("\nCLEANING SUMMARY")
        print("-" * 40)
        print("Invalid ages detected:", invalid_age_count)
        print("Invalid incomes detected:", invalid_income_count)
        print("Missing age values filled:", missing_age_count)
        print("Missing income values filled:", missing_income_count)
        print("Invalid emails detected:", invalid_email_count)
        print("Missing emails detected:", missing_email_count)
        print("Invalid phone numbers detected:", invalid_phone_count)
        print("Missing phone numbers detected:", missing_phone_count)
        print("Invalid purchase dates detected:", invalid_date_count)
        print("Missing purchase dates detected:", missing_date_count)
        print("Invalid purchase amounts detected:", invalid_purchase_amount_count)
        print("Missing purchase amounts detected:", missing_purchase_amount_count)
        print("Invalid Customer IDs detected:", invalid_customer_id_count)
        print("Missing Customer IDs detected:", missing_customer_id_count)
        print("Invalid genders detected:", invalid_gender_count)
        print("Missing genders detected:", missing_gender_count)
        print("Invalid cities detected:", invalid_city_count)
        print("Missing cities detected:", missing_city_count)

    return df

def main():
    """Preserve the original standalone cleaning workflow."""

    input_file = Path("data/raw/dirty_customer_data.csv")
    output_file = Path("data/processed/cleaned_data.csv")

    if not input_file.is_file():
        raise FileNotFoundError(
            f"Input CSV file not found: {input_file}"
        )

    df = pd.read_csv(input_file)

    cleaned_df = clean_dataframe(df, verbose=True)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cleaned_df.to_csv(output_file, index=False)

    print("Cleaned dataset saved successfully.")
    print("Output:", output_file)


if __name__ == "__main__":
    main()
