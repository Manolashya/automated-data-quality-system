
import json
from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_DATASET = PROJECT_ROOT / "data" / "raw" / "customer_data.csv"
PROFILE_REPORT = PROJECT_ROOT / "reports" / "profiling_report.json"


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Automated Data Quality Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Automated Data Quality Dashboard")
st.write(
    "Upload a CSV dataset to explore its structure, "
    "missing values, duplicates, and data quality."
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

try:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        dataset_name = uploaded_file.name
        using_default_dataset = False

    elif DEFAULT_DATASET.exists():
        df = pd.read_csv(DEFAULT_DATASET)
        dataset_name = DEFAULT_DATASET.name
        using_default_dataset = True

    else:
        st.error("Default dataset was not found.")
        st.stop()

except Exception as error:
    st.error(f"Could not read the CSV file: {error}")
    st.stop()


if df.empty:
    st.warning("The selected dataset is empty.")
    st.stop()


# --------------------------------------------------
# Dataset overview
# --------------------------------------------------

st.header("1. Dataset Overview")

st.write(f"**Dataset:** {dataset_name}")

row_count, column_count = df.shape
duplicate_count = int(df.duplicated().sum())
missing_count = int(df.isna().sum().sum())
total_cells = row_count * column_count

missing_percentage = (
    (missing_count / total_cells) * 100
    if total_cells > 0
    else 0
)

completeness_percentage = 100 - missing_percentage

metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric("Total Rows", row_count)
metric2.metric("Total Columns", column_count)
metric3.metric("Duplicate Rows", duplicate_count)
metric4.metric("Missing Values", missing_count)


# --------------------------------------------------
# Dataset preview
# --------------------------------------------------

st.header("2. Dataset Preview")

st.dataframe(df.head(10), width="stretch")

with st.expander("View complete dataset"):
    st.dataframe(df, width="stretch")


# --------------------------------------------------
# Missing value analysis
# --------------------------------------------------

st.header("3. Missing Value Analysis")

missing_by_column = df.isna().sum()

missing_report = pd.DataFrame({
    "Column": missing_by_column.index,
    "Missing Values": missing_by_column.values,
    "Missing Percentage": (
        missing_by_column.values / row_count
    ) * 100
})

st.dataframe(missing_report, width="stretch")

if missing_count > 0:
    st.bar_chart(
        missing_report.set_index("Column")["Missing Values"],
        width="stretch"
    )
else:
    st.success("No missing values found in this dataset.")


# --------------------------------------------------
# Column information
# --------------------------------------------------

st.header("4. Column Information")

column_report = pd.DataFrame({
    "Column": df.columns,
    "Data Type": [str(df[column].dtype) for column in df.columns],
    "Unique Values": [
        int(df[column].nunique(dropna=True))
        for column in df.columns
    ],
    "Missing Values": [
        int(df[column].isna().sum())
        for column in df.columns
    ]
})

st.dataframe(column_report, width="stretch")


# --------------------------------------------------
# Numerical summary
# --------------------------------------------------

st.header("5. Numerical Summary")

numerical_columns = df.select_dtypes(include="number")

if not numerical_columns.empty:
    st.dataframe(
        numerical_columns.describe(),
        width="stretch"
    )
else:
    st.info("No numerical columns are available.")


# --------------------------------------------------
# Dynamic profiling metrics
# --------------------------------------------------

st.header("6. Dynamic Data Profiling Report")

st.caption(
    "These metrics are calculated directly from the currently "
    "selected dataset, including uploaded CSV files."
)

profile1, profile2, profile3, profile4 = st.columns(4)

profile1.metric(
    "Overall Completeness",
    f"{completeness_percentage:.2f}%"
)

profile2.metric(
    "Missing Value Percentage",
    f"{missing_percentage:.2f}%"
)

profile3.metric(
    "Duplicate Rows",
    duplicate_count
)

profile4.metric(
    "Total Records",
    row_count
)


# --------------------------------------------------
# Per-column completeness
# --------------------------------------------------

st.subheader("Column Completeness")

column_completeness = (
    (1 - df.isna().sum() / row_count) * 100
)

completeness_report = pd.DataFrame({
    "Column": column_completeness.index,
    "Completeness Percentage": column_completeness.values
})

st.dataframe(completeness_report, width="stretch")

st.bar_chart(
    completeness_report.set_index("Column"),
    width="stretch"
)


# --------------------------------------------------
# Potential PII column detection
# --------------------------------------------------

st.subheader("Potential PII Columns")

pii_keywords = [
    "name",
    "email",
    "phone",
    "mobile",
    "address",
    "customer_id",
    "user_id",
    "ssn",
    "passport"
]

potential_pii_columns = [
    column
    for column in df.columns
    if any(
        keyword in str(column).lower()
        for keyword in pii_keywords
    )
]

if potential_pii_columns:
    st.write(potential_pii_columns)
else:
    st.info("No potential PII columns detected by the column-name check.")

st.caption(
    "Note: PII detection is based on column names only. "
    "It does not confirm whether a column contains personal information."
)


# --------------------------------------------------
# Saved project profiling report
# --------------------------------------------------

st.header("7. Saved Project Validation Report")

if using_default_dataset and PROFILE_REPORT.exists():

    try:
        with open(PROFILE_REPORT, "r", encoding="utf-8") as file:
            report = json.load(file)

        st.subheader("Overall Quality Score")

        quality_score = report.get("overall_quality_score", "N/A")

        if isinstance(quality_score, (int, float)):
            st.metric(
                "Data Quality Score",
                f"{quality_score:.2f}%"
            )
        else:
            st.write(quality_score)

        st.subheader("Validation Summary")

        validation_summary = report.get("validation_summary", {})

        if validation_summary:
            validation_df = pd.DataFrame({
                "Validation Check": list(validation_summary.keys()),
                "Score": list(validation_summary.values())
            })

            st.dataframe(validation_df, width="stretch")

            st.bar_chart(
                validation_df.set_index("Validation Check"),
                width="stretch"
            )
        else:
            st.info("No validation summary is available.")

        st.subheader("Saved PII Detection Results")

        saved_pii = report.get("pii_columns", [])

        if saved_pii:
            st.write(saved_pii)
        else:
            st.info("No saved PII columns were reported.")

    except (OSError, json.JSONDecodeError) as error:
        st.warning(f"Could not load the saved profiling report: {error}")

else:
    st.info(
        "The dynamic profiling metrics above were calculated for this "
        "uploaded dataset. The saved project validation report is "
        "available when using the default project dataset."
    )


# --------------------------------------------------
# Download dataset
# --------------------------------------------------

st.header("8. Download Dataset")

csv_data = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="dataset_download.csv",
    mime="text/csv"
)
