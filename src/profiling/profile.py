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
profiling_report = {
    "dataset_shape": {
        "rows": len(df),
        "columns": len(df.columns)
    },
    "columns": df.columns.tolist(),
    "data_types": df.dtypes.astype(str).to_dict(),
    "semantic_types": semantic_types,
    "missing_values": df.isnull().sum().to_dict(),
    "duplicate_rows": int(df.duplicated().sum()),
    "cardinality": df.nunique().to_dict(),
    "pii_columns": pii_columns
}

with open("reports/profiling_report.json", "w") as file:
    json.dump(profiling_report, file, indent=4)

print("\nProfiling report saved successfully.")