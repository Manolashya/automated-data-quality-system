import pandas as pd

input_file = "data/raw/dirty_customer_data.csv"
output_file = "data/processed/cleaned_data.csv"

df = pd.read_csv(input_file)

print("DATASET LOADED")
print("-" * 40)

print("Original Shape:", df.shape)

# Remove duplicate rows
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
if "Age" in df.columns:
    age_median = df["Age"].median()
    df["Age"]=df["Age"].fillna(age_median)
print("Missing Age values filled using median")

# Save cleaned dataset
df.to_csv(output_file, index=False)

print("Cleaned dataset saved successfully.")
print("Output:", output_file)