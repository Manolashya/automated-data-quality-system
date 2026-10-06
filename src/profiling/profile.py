import pandas as pd
import re
import sys
import json

# Path of the raw dataset
if len(sys.argv)>1:
 file_path=sys.argv[1]
else:
 file_path="data/raw/customer_data.csv"

# Load CSV into a DataFrame
df = pd.read_csv(file_path)

print("DATASET LOADED SUCCESSFULLY")
print("-" * 40)

# Number of rows and columns
print("Shape:", df.shape)

# Column names
print("\nColumns:")
print(df.columns.tolist())

# Data types
print("\nData Types:")
print(df.dtypes)

# Missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Duplicate rows
print("\nDuplicate Rows:")
print(df.duplicated().sum())
# Statistical summary of numerical columns
print("\nStatistical Summary:")
print(df.describe())
# Cardinality analysis
print("\nCardinality:")
for column in df.columns:
    print(column, ":", df[column].nunique(), "unique values")
# Value distribution for categorical columns
print("\nValue Distribution:")

for column in df.select_dtypes(include="str").columns:
    print("\n", column)
    print(df[column].value_counts())
# Correlation analysis
print("\nCorrelation Matrix:")

numeric_columns = df.select_dtypes(include="number")

print(numeric_columns.corr())
# Semantic column detection
print("\nSemantic Column Detection:")


def detect_semantic_type(column):
    name = column.lower()

    if "email" in name:
        return "Email"

    elif "phone" in name:
        return "Phone"

    elif "date" in name:
        return "Date"

    elif "name" in name:
        return "Name"

    elif "id" in name:
        return "ID"

    elif "gender" in name:
        return "Categorical"

    elif "city" in name:
        return "Categorical"

    elif "age" in name:
        return "Numeric"

    elif "income" in name:
        return "Numeric"

    elif "amount" in name:
        return "Numeric"

    else:
        return "Unknown"


for column in df.columns:
    semantic_type = detect_semantic_type(column)
    print(column, "→", semantic_type)
# Value-based email detection
print("\nValue-Based Email Detection:")

email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

for column in df.columns:
    for value in df[column].dropna():
        if re.match(email_pattern, str(value)):
            print(column, "→ Email")
            break
# Value-based phone detection
print("\nValue-Based Phone Detection:")

phone_pattern = r"^\d{10}$"

for column in df.columns:
    for value in df[column].dropna():
        if re.match(phone_pattern, str(value)):
            print(column, "→ Phone")
            break
# PII Column Detection
print("\nPII Column Detection:")

pii_columns = []

for column in df.columns:
    column_name = column.lower()

    if (
        "name" in column_name
        or "email" in column_name
        or "phone" in column_name
        or "mobile" in column_name
        or "customer_id" in column_name
    ):
        pii_columns.append(column)

print("PII Columns:", pii_columns)
# Mixed-Type Detection
print("\nMixed-Type Detection:")

for column in df.columns:
    types = df[column].dropna().map(type).value_counts()

    if len(types) > 1:
        print(column, "→ Mixed Types:", types.to_dict())
    else:
        print(column, "→ Consistent Type")
# Missing-Value Matrix
print("\nMissing-Value Matrix:")

missing_matrix = pd.DataFrame({
    "Missing Count": df.isnull().sum(),
    "Missing Percentage": (df.isnull().sum() / len(df)) * 100,
    "Total Values": len(df)
})

print(missing_matrix)
# Type Consistency Check
print("\nType Consistency Check:")

for column in df.columns:
    semantic_type = detect_semantic_type(column)
    actual_type = str(df[column].dtype)

    if semantic_type == "Numeric" and actual_type in ["int64", "float64"]:
        status = "Consistent"

    elif semantic_type in ["Name", "Email", "Phone", "ID", "Categorical", "Date"] and actual_type in ["str", "object", "int64"]:
        status = "Consistent"

    else:
        status = "Needs Attention"

    print(
        column,
        "→ Semantic:",
        semantic_type,
        "| Actual:",
        actual_type,
        "|",
        status
    )
# Suspicious Column Detection
print("\nSuspicious Column Detection:")

for column in df.columns:
    unique_count = df[column].nunique()
    total_count = len(df)

    uniqueness_ratio = unique_count / total_count
    semantic_type = detect_semantic_type(column)

    if uniqueness_ratio == 1.0 and semantic_type == "ID":
        print(column, "→ Highly Unique | Possible Identifier")

    elif column in pii_columns:
        print(column, "→ PII Column | Needs Attention")
# Save Profiling Report
import json
semantic_types={}
for column in df.columns:
     semantic_types[column]=detect_semantic_type(column)
missing_percentage=(df.isnull().sum()/len(df)*100).round(2)
unique_percentage = (
    df.nunique() / len(df) * 100
).round(2)
completeness_score = ((df.notnull().sum() / len(df)) * 100).round(2)
email_validity = None
if "Email" in df.columns:
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    valid_emails = df["Email"].dropna().astype(str).str.match(email_pattern)
    email_validity = round(valid_emails.sum() / len(valid_emails) * 100, 2)
phone_validity = None
if "Phone" in df.columns:
    phone_pattern = r"^[6-9]\d{9}$"
    valid_phones = df["Phone"].dropna().astype(str).str.match(phone_pattern)
    phone_validity = round(valid_phones.sum() / len(valid_phones) * 100, 2)
date_validity = None
if "Purchase_Date" in df.columns:
    valid_dates = pd.to_datetime(df["Purchase_Date"], errors="coerce")
    date_validity = round(valid_dates.notnull().sum() / len(valid_dates) * 100,2)
age_validity = None
age_validity = None
if "Age" in df.columns:
    valid_ages = df["Age"].dropna().between(0, 100)
    age_validity = round(valid_ages.sum() / len(valid_ages) * 100,2)
income_validity = None
if "Income" in df.columns:
    valid_income = df["Income"].dropna() >= 0
    income_validity = round(valid_income.sum() / len(valid_income) * 100,2)
purchase_amount_validity = None

if "Purchase_Amount" in df.columns:
    valid_purchase_amounts = df["Purchase_Amount"].dropna() >= 0

    purchase_amount_validity = round(
        valid_purchase_amounts.sum() / len(valid_purchase_amounts) * 100,
        2
    )
gender_validity = None

if "Gender" in df.columns:
    allowed_genders = ["Male", "Female"]

    valid_genders = df["Gender"].dropna().isin(allowed_genders)

    gender_validity = round(valid_genders.sum() / len(valid_genders) *100,2)
city_validity = None

if "City" in df.columns:
    allowed_cities = ["Hyderabad", "Bangalore", "Chennai"]

    valid_cities = df["City"].dropna().isin(allowed_cities)

    city_validity = round(
        valid_cities.sum() / len(valid_cities) * 100,
        2
    )
customer_id_validity = None

if "Customer_ID" in df.columns:
    customer_id_pattern = r"^C\d{3}$"

    valid_customer_ids = (
        df["Customer_ID"]
        .dropna()
        .astype(str)
        .str.match(customer_id_pattern)
    )

    customer_id_validity = round(
        valid_customer_ids.sum() / len(valid_customer_ids) * 100,
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
    "customer_id": customer_id_validity
}
overall_quality_score = round(
    sum(validation_summary.values()) / len(validation_summary),
    2
)

profiling_report = {
    "dataset_shape": {
        "rows": len(df),
        "columns": len(df.columns)
    },
    "columns": df.columns.tolist(),
    "data_types": df.dtypes.astype(str).to_dict(),
    "semantic_types": semantic_types,
    "missing_values": df.isnull().sum().to_dict(),
    "missing_percentage": missing_percentage.to_dict(),
    "unique_percentage":unique_percentage.to_dict(),
    "completeness_score": completeness_score.to_dict(),
    "email_validity_percentage": email_validity,
    "phone_validity_percentage": phone_validity,
    "date_validity_percentage": date_validity,
    "age_validity_percentage": age_validity,
    "income_validity_percentage": income_validity,
    "purchase_amount_validity_percentage": purchase_amount_validity,
    "gender_validity_percentage": gender_validity,
    "city_validity_percentage": city_validity,
    "customer_id_validity_percentage": customer_id_validity,
    "validation_summary": validation_summary,
    "overall_quality_score": overall_quality_score,
    "duplicate_rows": int(df.duplicated().sum()),
    "cardinality": df.nunique().to_dict(),
    "pii_columns": pii_columns
}

with open("reports/profiling_report.json", "w") as file:
    json.dump(profiling_report, file, indent=4)

print("\nProfiling report saved successfully.")