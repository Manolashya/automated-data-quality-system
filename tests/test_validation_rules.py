
import pandas as pd

from src.validation.rules import validate_dataframe


def valid_customer_data():
    return pd.DataFrame({
        "Customer_ID": ["C001", "C002"],
        "Name": ["Rahul Kumar", "Priya Sharma"],
        "Age": [25, 30],
        "Email": ["rahul@gmail.com", "priya@gmail.com"],
        "Phone": [9876543210, 9876543211],
        "Gender": ["Male", "Female"],
        "City": ["Hyderabad", "Bangalore"],
        "Income": [40000, 50000],
        "Purchase_Amount": [2000, 3000],
        "Purchase_Date": ["2026-08-15", "2026-08-16"],
    })


def test_valid_dataset_has_no_issues():
    df = valid_customer_data()

    issues = validate_dataframe(df)

    assert issues == []


def test_missing_required_value_is_detected():
    df = valid_customer_data()
    df.loc[0, "Name"] = None

    issues = validate_dataframe(df)

    assert any(
        issue["column"] == "Name"
        and issue["rule"] == "missing_value"
        for issue in issues
    )


def test_invalid_age_is_detected():
    df = valid_customer_data()
    df.loc[0, "Age"] = 150

    issues = validate_dataframe(df)

    assert any(
        issue["column"] == "Age"
        and issue["rule"] == "age_range"
        for issue in issues
    )


def test_non_numeric_age_is_detected():
    df = valid_customer_data()
    df["Age"] = df["Age"].astype(object)
    df.loc[0, "Age"] = "unknown"

    issues = validate_dataframe(df)

    assert any(
        issue["column"] == "Age"
        and issue["rule"] == "numeric"
        for issue in issues
    )

def test_invalid_email_is_detected():
    df = valid_customer_data()
    df.loc[0, "Email"] = "invalid-email"

    issues = validate_dataframe(df)

    assert any(
        issue["column"] == "Email"
        and issue["rule"] == "email_format"
        for issue in issues
    )


def test_negative_income_is_detected():
    df = valid_customer_data()
    df.loc[0, "Income"] = -5000

    issues = validate_dataframe(df)

    assert any(
        issue["column"] == "Income"
        and issue["rule"] == "non_negative"
        for issue in issues
    )


def test_negative_purchase_amount_is_detected():
    df = valid_customer_data()
    df.loc[0, "Purchase_Amount"] = -100

    issues = validate_dataframe(df)

    assert any(
        issue["column"] == "Purchase_Amount"
        and issue["rule"] == "non_negative"
        for issue in issues
    )


def test_invalid_gender_is_detected():
    df = valid_customer_data()
    df.loc[0, "Gender"] = "Other"

    issues = validate_dataframe(df)

    assert any(
        issue["column"] == "Gender"
        and issue["rule"] == "allowed_values"
        for issue in issues
    )


def test_missing_required_column_is_detected():
    df = valid_customer_data().drop(columns=["Email"])

    issues = validate_dataframe(df)

    assert any(
        issue["column"] == "Email"
        and issue["rule"] == "required_column"
        for issue in issues
    )
