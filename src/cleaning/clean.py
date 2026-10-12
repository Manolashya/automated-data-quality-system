
import pandas as pd
from pathlib import Path

input_file = "data/raw/dirty_customer_data.csv"
output_file = "data/processed/cleaned_data.csv"

df = pd.read_csv(input_file)
# Ensure Age and Income contain numeric values
for column in ["Age", "Income"]:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

print("DATASET LOADED")
print("-" * 40)


print("Original Shape:", df.shape)

# Detect repeated Customer_ID values before removing exact duplicates
if "Customer_ID" in df.columns:
    customer_ids = df["Customer_ID"].astype("string").str.strip()

    duplicate_customer_mask = (
        customer_ids.notna()
        & customer_ids.duplicated(keep=False)
    )

    duplicate_customer_ids = sorted(
        customer_ids[duplicate_customer_mask].unique().tolist()
    )

    print(
        "Rows with repeated Customer_ID:",
        int(duplicate_customer_mask.sum())
    )
    print("Repeated Customer_ID values:", duplicate_customer_ids)

# Remove exact duplicate rows
df = df.drop_duplicates()

print("After Duplicate Removal:", df.shape)


# Remove extra spaces from text columns
text_columns = df.select_dtypes(include="str").columns

for column in text_columns:
    df[column] = df[column].str.strip()

print("Whitespace cleaned")

# Normalize Gender values
if "Gender" in df.columns:
    df["Gender"] = df["Gender"].replace({
        "M": "Male",
        "F": "Female"
    })

print("Gender values normalized")

# Count and handle invalid Age values
invalid_age_count = 0

if "Age" in df.columns:
    invalid_ages = (
        df["Age"].notna() &
        ~df["Age"].between(0, 100)
    )

    invalid_age_count = int(invalid_ages.sum())

    df.loc[invalid_ages, "Age"] = float("nan")

    print("Invalid Age values handled")

# Count and handle invalid Income values
invalid_income_count = 0

if "Income" in df.columns:
    invalid_incomes = (
        df["Income"].notna() &
        (df["Income"] < 0)
    )

    invalid_income_count = int(invalid_incomes.sum())

    df.loc[invalid_incomes, "Income"] = float("nan")

    print("Invalid Income values handled")


# Handle missing Age values
missing_age_count = 0

if "Age" in df.columns:
    missing_age_count = int(df["Age"].isna().sum())
    age_median = df["Age"].median()

    if pd.notna(age_median):
        df["Age"] = df["Age"].fillna(age_median)
        print("Missing Age values filled using median")
    elif missing_age_count > 0:
        print("Warning: Age contains only missing values; median imputation is not possible")

# Handle missing Income values
missing_income_count = 0

if "Income" in df.columns:
    missing_income_count = int(df["Income"].isna().sum())
    income_median = df["Income"].median()

    if pd.notna(income_median):
        df["Income"] = df["Income"].fillna(income_median)
        print("Missing Income values filled using median")
    elif missing_income_count > 0:
        print("Warning: Income contains only missing values; median imputation is not possible")

# Detect invalid and missing Email values
invalid_email_count = 0
missing_email_count = 0

if "Email" in df.columns:
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    missing_email_count = int(df["Email"].isna().sum())

    valid_email_mask = df["Email"].str.match(
        email_pattern,
        na=False
    )

    invalid_email_count = int(
        (~valid_email_mask & df["Email"].notna()).sum()
    )

    print("Email validation completed")
# Detect invalid and missing Phone values
invalid_phone_count = 0
missing_phone_count = 0

if "Phone" in df.columns:
    phone_pattern = r"^[6-9]\d{9}$"

    phone_values = df["Phone"].astype("string").str.strip()

    missing_phone_count = int(phone_values.isna().sum())

    valid_phone_mask = phone_values.str.match(
        phone_pattern,
        na=False
    )

    invalid_phone_count = int(
        (~valid_phone_mask & phone_values.notna()).sum()
    )

    print("Phone validation completed")
# Detect invalid and missing Purchase_Date values
invalid_date_count = 0
missing_date_count = 0

if "Purchase_Date" in df.columns:
    date_values = df["Purchase_Date"].astype("string").str.strip()

    missing_date_count = int(date_values.isna().sum())

    parsed_dates = pd.to_datetime(
        date_values,
        format="%Y-%m-%d",
        errors="coerce"
    )

    invalid_date_count = int(
        (parsed_dates.isna() & date_values.notna()).sum()
    )

    print("Purchase date validation completed")
# Detect invalid and missing Purchase_Amount values
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

    print("Purchase amount validation completed")
# Detect invalid and missing Customer_ID values
invalid_customer_id_count = 0
missing_customer_id_count = 0

if "Customer_ID" in df.columns:
    customer_ids = df["Customer_ID"].astype("string").str.strip()

    missing_customer_id_count = int(customer_ids.isna().sum())

    valid_id_mask = customer_ids.str.match(
        r"^C\d{3}$",
        na=False
    )

    invalid_customer_id_count = int(
        (~valid_id_mask & customer_ids.notna()).sum()
    )

    print("Customer ID validation completed")
# Detect invalid and missing Gender values
invalid_gender_count = 0
missing_gender_count = 0

if "Gender" in df.columns:
    gender_values = df["Gender"].astype("string").str.strip()

    missing_gender_count = int(gender_values.isna().sum())

    valid_gender_mask = gender_values.isin(["Male", "Female"])

    invalid_gender_count = int(
        (~valid_gender_mask & gender_values.notna()).sum()
    )

    print("Gender validation completed")


# Detect invalid and missing City values
invalid_city_count = 0
missing_city_count = 0

if "City" in df.columns:
    city_values = df["City"].astype("string").str.strip()

    missing_city_count = int(city_values.isna().sum())

    valid_city_mask = city_values.isin([
        "Hyderabad",
        "Bangalore",
        "Chennai"
    ])

    invalid_city_count = int(
        (~valid_city_mask & city_values.notna()).sum()
    )

    print("City validation completed")

# Print cleaning summary
print("\nCLEANING SUMMARY")
print("-" * 40)
print("Invalid ages detected:", invalid_age_count)
print("Invalid incomes detected:", invalid_income_count)
print("Missing age values filled:", missing_age_count)
print("Missing income values filled:",missing_income_count)
print("Invalid emails detected:", invalid_email_count)
print("Missing emails detected:", missing_email_count)
print("Invalid phone numbers detected:", invalid_phone_count)
print("Missing phone numbers detected:",missing_phone_count)
print("Invalid purchase dates detected:",invalid_date_count)
print("Missing purchase dates detected:", missing_date_count)
print("Invalid purchase amounts detected:",invalid_purchase_amount_count)
print("Missing purchase amounts detected:",missing_purchase_amount_count)
print("Invalid Customer IDs detected:", invalid_customer_id_count)
print("Missing Customer IDs detected:", missing_customer_id_count)
print("Invalid genders detected:", invalid_gender_count)
print("Missing genders detected:", missing_gender_count)
print("Invalid cities detected:",invalid_city_count)
print("Missing cities detected:", missing_city_count)

# Save cleaned dataset
# Create the output folder if it does not exist
Path(output_file).parent.mkdir(parents=True, exist_ok=True)

# Save cleaned dataset
df.to_csv(output_file, index=False)

print("Cleaned dataset saved successfully.")
print("Output:", output_file)
