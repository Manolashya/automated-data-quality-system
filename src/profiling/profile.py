
import json
import re
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def detect_semantic_type(column):
    name = str(column).lower()

    if "email" in name:
        return "Email"
    elif "phone" in name:
        return "Phone"
    elif "date" in name:
        return "Date"
    elif "gender" in name or "city" in name:
        return "Categorical"
    elif "age" in name or "income" in name or "amount" in name:
        return "Numeric"
    elif name == "customer_id" or name.endswith("_id"):
        return "ID"
    elif "name" in name:
        return "Name"
    else:
        return "Unknown"


def profile_dataframe(
    df,
    file_name="uploaded_dataset.csv",
    verbose=True
):
    """
    Generate a profiling report for an existing DataFrame.

    Parameters:
        df: pandas DataFrame to profile.
        file_name: Name of the source dataset.
        verbose: Whether to print profiling details.

    Returns:
        Dictionary containing the profiling report.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Input DataFrame contains no data rows.")

    def log(*args, **kwargs):
        if verbose:
            print(*args, **kwargs)

    log("DATASET LOADED SUCCESSFULLY")
    log("-" * 40)
    log("Shape:", df.shape)

    log("\nColumns:")
    log(df.columns.tolist())

    log("\nData Types:")
    log(df.dtypes)

    log("\nMissing Values:")
    log(df.isnull().sum())

    log("\nDuplicate Rows:")
    log(df.duplicated().sum())

    log("\nStatistical Summary:")
    log(df.describe())

    log("\nCardinality:")
    for column in df.columns:
        log(column, ":", df[column].nunique(), "unique values")

    log("\nValue Distribution:")
    for column in df.select_dtypes(include="str").columns:
        log("\n", column)
        log(df[column].value_counts())

    log("\nCorrelation Matrix:")
    numeric_columns = df.select_dtypes(include="number")
    log(numeric_columns.corr())

    log("\nSemantic Column Detection:")
    for column in df.columns:
        log(f"{column}: {detect_semantic_type(column)}")

    # Value-based email detection
    log("\nValue-Based Email Detection:")
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    for column in df.columns:
        values = df[column].dropna().astype(str)
        if values.str.match(email_pattern).any():
            log(column, "→ Email")

    # Value-based phone detection
    log("\nValue-Based Phone Detection:")
    phone_pattern = r"^\d{10}$"

    for column in df.columns:
        values = df[column].dropna().astype(str)
        if values.str.match(phone_pattern).any():
            log(column, "→ Phone")

    # Mixed-type detection
    log("\nMixed-Type Detection:")

    for column in df.columns:
        types = df[column].dropna().map(type).value_counts()

        if len(types) > 1:
            log(column, "→ Mixed Types:", types.to_dict())
        else:
            log(column, "→ Consistent Type")

    # Missing-value matrix
    log("\nMissing-Value Matrix:")

    missing_matrix = pd.DataFrame({
        "Missing Count": df.isnull().sum(),
        "Missing Percentage": (
            df.isnull().sum() / len(df)
        ) * 100,
        "Total Values": len(df)
    })

    log(missing_matrix)

    # Type consistency check
    log("\nType Consistency Check:")

    for column in df.columns:
        semantic_type = detect_semantic_type(column)
        actual_type = str(df[column].dtype)

        if (
            semantic_type == "Numeric"
            and pd.api.types.is_numeric_dtype(df[column])
        ):
            status = "Consistent"

        elif semantic_type in [
            "Name", "Email", "Phone", "ID",
            "Categorical", "Date"
        ]:
            status = (
                "Consistent"
                if actual_type in [
                    "str", "object", "int64", "string"
                ]
                else "Needs Attention"
            )
        else:
            status = "Needs Attention"

        log(
            column,
            "→ Semantic:", semantic_type,
            "| Actual:", actual_type,
            "|", status
        )

    # Validation summary
    email_validity = None

    if "Email" in df.columns:
        email_values = df["Email"].dropna().astype(str)

        if len(email_values) > 0:
            email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
            email_validity = round(
                email_values.str.match(email_pattern).mean() * 100,
                2
            )

    phone_validity = None

    if "Phone" in df.columns:
        phone_values = df["Phone"].dropna().astype(str)

        if len(phone_values) > 0:
            phone_pattern = r"^[6-9]\d{9}$"
            phone_validity = round(
                phone_values.str.match(phone_pattern).mean() * 100,
                2
            )

    date_validity = None

    if "Purchase_Date" in df.columns:
        date_values = df["Purchase_Date"].dropna()

        if len(date_values) > 0:
            valid_dates = pd.to_datetime(
                date_values, errors="coerce"
            )
            date_validity = round(
                valid_dates.notna().mean() * 100, 2
            )

    age_validity = None

    if "Age" in df.columns:
        age_values = pd.to_numeric(
            df["Age"], errors="coerce"
        ).dropna()

        if len(age_values) > 0:
            age_validity = round(
                age_values.between(0, 100).mean() * 100, 2
            )

    income_validity = None

    if "Income" in df.columns:
        income_values = pd.to_numeric(
            df["Income"], errors="coerce"
        ).dropna()

        if len(income_values) > 0:
            income_validity = round(
                (income_values >= 0).mean() * 100, 2
            )

    purchase_amount_validity = None

    if "Purchase_Amount" in df.columns:
        amount_values = pd.to_numeric(
            df["Purchase_Amount"], errors="coerce"
        ).dropna()

        if len(amount_values) > 0:
            purchase_amount_validity = round(
                (amount_values >= 0).mean() * 100, 2
            )

    gender_validity = None

    if "Gender" in df.columns:
        gender_values = df["Gender"].dropna()

        if len(gender_values) > 0:
            gender_validity = round(
                gender_values.isin(
                    ["Male", "Female", "M", "F"]
                ).mean() * 100,
                2
            )

    city_validity = None

    if "City" in df.columns:
        city_values = df["City"].dropna()

        if len(city_values) > 0:
            city_validity = round(
                city_values.isin(
                    ["Hyderabad", "Bangalore", "Chennai"]
                ).mean() * 100,
                2
            )

    customer_id_validity = None

    if "Customer_ID" in df.columns:
        customer_ids = (
            df["Customer_ID"].dropna().astype(str)
        )

        if len(customer_ids) > 0:
            customer_id_validity = round(
                customer_ids.str.match(
                    r"^C\d{3}$"
                ).mean() * 100,
                2
            )

    validation_summary = {
        "email": email_validity,
        "phone": phone_validity,
        "date": date_validity,
        "age": age_validity,
        "income": income_validity,
        "purchase_amount": purchase_amount_validity,
        "gender": gender_validity,
        "city": city_validity,
        "customer_id": customer_id_validity,
    }

    valid_scores = [
        score
        for score in validation_summary.values()
        if score is not None
    ]

    overall_quality_score = (
        round(
            sum(valid_scores) / len(valid_scores), 2
        )
        if valid_scores else None
    )

    # PII detection
    log("\nPII Column Detection:")

    pii_columns = []

    for column in df.columns:
        column_name = str(column).lower()

        if any(
            keyword in column_name
            for keyword in (
                "name", "email", "phone",
                "mobile", "customer_id"
            )
        ):
            pii_columns.append(column)

    log("PII Columns:", pii_columns)

    # Suspicious-column detection
    log("\nSuspicious Column Detection:")

    for column in df.columns:
        unique_count = df[column].nunique()
        uniqueness_ratio = unique_count / len(df)
        semantic_type = detect_semantic_type(column)

        if (
            uniqueness_ratio == 1.0
            and semantic_type == "ID"
        ):
            log(
                column,
                "→ Highly Unique | Possible Identifier"
            )

        elif column in pii_columns:
            log(column, "→ PII Column | Needs Attention")

    # Build profiling report
    row_count = len(df)

    missing_percentage = (
        df.isnull().sum() / row_count * 100
    ).round(2)

    unique_percentage = (
        df.nunique() / row_count * 100
    ).round(2)

    completeness_score = (
        df.notnull().sum() / row_count * 100
    ).round(2)

    report = {
        "file_name": Path(str(file_name)).name,
        "rows": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "dataset_shape": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
        },
        "columns": df.columns.tolist(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "semantic_types": {
            str(column): detect_semantic_type(column)
            for column in df.columns
        },
        "missing_values": {
            str(column): int(count)
            for column, count in df.isnull().sum().items()
        },
        "missing_percentage": {
            str(column): float(value)
            for column, value in missing_percentage.items()
        },
        "unique_percentage": {
            str(column): float(value)
            for column, value in unique_percentage.items()
        },
        "completeness_score": {
            str(column): float(value)
            for column, value in completeness_score.items()
        },
        "email_validity_percentage": email_validity,
        "phone_validity_percentage": phone_validity,
        "date_validity_percentage": date_validity,
        "age_validity_percentage": age_validity,
        "income_validity_percentage": income_validity,
        "purchase_amount_validity_percentage": (
            purchase_amount_validity
        ),
        "gender_validity_percentage": gender_validity,
        "city_validity_percentage": city_validity,
        "customer_id_validity_percentage": (
            customer_id_validity
        ),
        "validation_summary": validation_summary,
        "overall_quality_score": overall_quality_score,
        "duplicate_rows": int(df.duplicated().sum()),
        "cardinality": {
            str(column): int(count)
            for column, count in df.nunique().items()
        },
        "pii_columns": pii_columns,
    }

    log("\nValidation Summary:")
    log(json.dumps(validation_summary, indent=4))

    log("\nOverall Quality Score:", overall_quality_score)
    log("PII Columns:", pii_columns)

    return report


def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "data/raw/customer_data.csv"

    input_path = Path(file_path)

    if not input_path.is_file():
        sys.exit(
            f"Error: Input CSV file not found: {file_path}"
        )

    try:
        df = pd.read_csv(input_path)

    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError
    ) as error:
        sys.exit(
            f"Error: Unable to read the input CSV file: {error}"
        )

    if df.empty:
        sys.exit(
            "Error: Input CSV contains no data rows."
        )

    report = profile_dataframe(
        df,
        file_name=input_path.name
    )

    report_dir = Path("reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / "profiling_report.json"

    with report_path.open(
        "w", encoding="utf-8"
    ) as report_file:
        json.dump(
            report,
            report_file,
            indent=4,
            allow_nan=False
        )

    print("Profiling report saved successfully.")


if __name__ == "__main__":
    main()
