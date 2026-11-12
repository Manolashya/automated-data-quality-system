
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# Project paths and pipeline import
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.runner import run_pipeline
from src.history.history_comparator import compare_quality_history
from src.recommendations.recommendation_engine import generate_recommendations

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
    type=["csv"],
    key="main_dataset"
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
# Download original dataset
# --------------------------------------------------

st.header("8. Download Dataset")

csv_data = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="dataset_download.csv",
    mime="text/csv"
)


# --------------------------------------------------
# Integrated data quality pipeline
# --------------------------------------------------

st.header("9. Integrated Data Quality Pipeline")

st.write(
    "Run cleaning, validation, profiling, anomaly detection, "
    "fuzzy duplicate detection, and optional data drift analysis "
    "on the selected dataset."
)

st.info(
    "The current pipeline is designed around the project's "
    "customer dataset structure. Other CSV files may need the "
    "expected columns and data formats."
)

reference_file = st.file_uploader(
    "Optional: Upload a reference CSV for data drift detection",
    type=["csv"],
    key="reference_dataset"
)

if st.button("Run Data Quality Pipeline", type="primary"):

    try:
        reference_df = None

        if reference_file is not None:
            reference_df = pd.read_csv(reference_file)

            if reference_df.empty:
                st.error("The reference dataset is empty.")
                st.stop()

        with st.spinner("Running the data quality pipeline..."):

            pipeline_results = run_pipeline(
                df.copy(),
                reference_df=reference_df
            )

        st.session_state["pipeline_results"] = pipeline_results
        st.session_state["pipeline_dataset_name"] = dataset_name

        st.success("Data quality pipeline completed successfully!")

    except Exception as error:
        st.error(f"Pipeline execution failed: {error}")


# --------------------------------------------------
# Display pipeline results
# --------------------------------------------------

if "pipeline_results" in st.session_state:

    results = st.session_state["pipeline_results"]

    st.subheader("Pipeline Execution Results")

    if st.session_state.get("pipeline_dataset_name") != dataset_name:
        st.warning(
            "These results belong to a previously selected dataset. "
            "Run the pipeline again to update them."
        )

    cleaned_df = results["cleaned_data"]

    original_rows = len(df)
    cleaned_rows = len(cleaned_df)

    validation_issues = results["validation_issues"]
    anomaly_results = results["anomaly_results"]
    duplicate_results = results["duplicate_results"]
    drift_results = results["drift_results"]

    anomaly_count = int(
        (anomaly_results["Anomaly"] == "Anomaly").sum()
    )

    result1, result2, result3, result4 = st.columns(4)

    result1.metric("Original Rows", original_rows)
    result2.metric("Cleaned Rows", cleaned_rows)
    result3.metric("Validation Issues", len(validation_issues))
    result4.metric("Anomalies Detected", anomaly_count)

    # Cleaned dataset

    st.subheader("Cleaned Dataset")

    st.dataframe(cleaned_df, width="stretch")

    cleaned_csv = cleaned_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Cleaned Dataset",
        data=cleaned_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
        key="download_cleaned_dataset"
    )
        # HTML report download

    html_report_path = results["html_report_path"]

    with open(html_report_path, "rb") as report_file:
        html_report = report_file.read()

    st.download_button(
        label="Download HTML Quality Report",
        data=html_report,
        file_name="data_quality_report.html",
        mime="text/html",
        key="download_html_report"
    )

    # Validation issues

    st.subheader("Validation Results")

    if validation_issues:
        validation_df = pd.DataFrame(validation_issues)
        st.warning(f"{len(validation_issues)} validation issue(s) found.")
        st.dataframe(validation_df, width="stretch")
    else:
        st.success("No validation issues found.")

    # Anomaly detection

    st.subheader("Anomaly Detection Results")

    if anomaly_count > 0:
        detected_anomalies = anomaly_results[
            anomaly_results["Anomaly"] == "Anomaly"
        ]

        st.warning(f"{anomaly_count} anomalous record(s) detected.")

        st.dataframe(
            detected_anomalies,
            width="stretch"
        )
    else:
        st.success("No anomalies detected.")

    with st.expander("View complete anomaly analysis"):
        st.dataframe(anomaly_results, width="stretch")

    # Fuzzy duplicate detection

    st.subheader("Fuzzy Duplicate Detection Results")

    if duplicate_results:
        duplicate_df = pd.DataFrame(duplicate_results)
        st.warning(
            f"{len(duplicate_results)} possible fuzzy duplicate pair(s) found."
        )
        st.dataframe(duplicate_df, width="stretch")
    else:
        st.success("No fuzzy duplicate pairs detected.")

    # Data drift detection

    st.subheader("Data Drift Detection Results")

    if reference_file is None:
        st.info(
            "Data drift analysis was not performed. "
            "Upload a reference CSV and run the pipeline again to compare datasets."
        )

    elif drift_results:
        drift_df = pd.DataFrame(drift_results)
        st.dataframe(drift_df, width="stretch")
    else:
        st.success("No data drift results were reported.")
# --------------------------------------------------
# 10. Quality History
# --------------------------------------------------

st.header("10. Quality History")

QUALITY_HISTORY = (
    PROJECT_ROOT / "reports" / "quality_history.csv"
)

if not QUALITY_HISTORY.exists():

    st.info(
        "No quality history is available yet. "
        "Run the data quality pipeline to create your first record."
    )

else:

    try:
        history_df = pd.read_csv(QUALITY_HISTORY)

        required_columns = [
            "timestamp",
            "dataset_name",
            "rows",
            "columns",
            "quality_score",
            "completeness",
            "missing_values",
            "duplicate_rows",
            "validation_issues",
            "anomalies",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in history_df.columns
        ]

        if missing_columns:

            st.warning(
                f"History file is missing columns: {missing_columns}"
            )

        elif history_df.empty:

            st.info("The quality history file contains no records.")

        else:

            # Prepare timestamps and quality scores
            history_df["parsed_timestamp"] = pd.to_datetime(
                history_df["timestamp"],
                errors="coerce",
                utc=True
            )

            history_df["quality_score"] = pd.to_numeric(
                history_df["quality_score"],
                errors="coerce"
            )

            valid_history = history_df.dropna(
                subset=["parsed_timestamp", "quality_score"]
            ).sort_values("parsed_timestamp")

            if valid_history.empty:

                st.info("No valid quality history records are available.")
            else:

                # Filter quality history by dataset
                dataset_options = [
                    "All Datasets"
                ] + sorted(
                    valid_history["dataset_name"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                selected_dataset = st.selectbox(
                    "Select Dataset",
                    options=dataset_options,
                    key="quality_history_dataset_filter"
                )

                if selected_dataset != "All Datasets":
                    valid_history = valid_history[
                        valid_history["dataset_name"] == selected_dataset
                    ].copy()

                # Latest execution metrics
                latest_record = valid_history.iloc[-1]

                history_metric1, history_metric2, history_metric3 = (
                    st.columns(3)
                )

                history_metric1.metric(
                    "Latest Quality Score",
                    f"{latest_record['quality_score']:.2f}%"
                )

                history_metric2.metric(
                    "Total Executions",
                    len(valid_history)
                )

                history_metric3.metric(
                    "Latest Dataset",
                    latest_record["dataset_name"]
                )

                # Quality score trend
                st.subheader("Quality Score Trend")

                quality_trend = valid_history.set_index(
                    "parsed_timestamp"
                )[["quality_score"]]

                st.line_chart(
                    quality_trend,
                    width="stretch"
                )

                # Complete execution history
                st.subheader("Execution History")

                history_display = valid_history[
                    required_columns
                ].sort_values(
                    "timestamp",
                    ascending=False
                )

                st.dataframe(
                    history_display,
                    width="stretch",
                    hide_index=True
                )

    except (OSError, pd.errors.ParserError, UnicodeError) as error:

        st.warning(
            f"Could not load quality history: {error}"
        )
# --------------------------------------------------
# 11. Quality Improvement Analysis
# --------------------------------------------------

st.header("11. Quality Improvement Analysis")

try:

    comparison_result = compare_quality_history()

    previous_execution = comparison_result["previous_execution"]
    latest_execution = comparison_result["latest_execution"]
    metric_comparison = comparison_result["comparison"]

    st.subheader("Execution Comparison")

    comparison_col1, comparison_col2 = st.columns(2)

    comparison_col1.metric(
        "Previous Quality Score",
        f"{previous_execution['quality_score']:.2f}%"
    )

    quality_difference = metric_comparison["quality_score"]["difference"]

    quality_difference = metric_comparison["quality_score"]["difference"]
    quality_delta = (
        f"{quality_difference:+.2f} percentage points"
        if quality_difference != 0
        else None
        )
    comparison_col2.metric(
        "Latest Quality Score",
        f"{latest_execution['quality_score']:.2f}%",
        delta=quality_delta
        )

    st.subheader("Metric Improvement Analysis")

    comparison_rows = []

    metric_labels = {
        "quality_score": "Quality Score",
        "completeness": "Completeness",
        "missing_values": "Missing Values",
        "duplicate_rows": "Duplicate Rows",
        "validation_issues": "Validation Issues",
        "anomalies": "Anomalies",
    }

    for metric, values in metric_comparison.items():

        comparison_rows.append({
            "Metric": metric_labels[metric],
            "Previous": values["previous"],
            "Latest": values["latest"],
            "Difference": values["difference"],
            "Status": values["status"].capitalize(),
        })

    comparison_display = pd.DataFrame(comparison_rows)

    st.dataframe(
        comparison_display,
        width="stretch",
        hide_index=True
    )

    improved_count = sum(
        values["status"] == "improved"
        for values in metric_comparison.values()
    )

    regressed_count = sum(
        values["status"] == "regressed"
        for values in metric_comparison.values()
    )

    unchanged_count = sum(
        values["status"] == "unchanged"
        for values in metric_comparison.values()
    )

    st.subheader("Overall Improvement Summary")

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    summary_col1.metric("Improved Metrics", improved_count)
    summary_col2.metric("Regressed Metrics", regressed_count)
    summary_col3.metric("Unchanged Metrics", unchanged_count)

    if improved_count > 0 and regressed_count == 0:

        st.success(
            "Data quality has improved compared with the previous execution."
        )

    elif regressed_count > 0:

        st.warning(
            "Some data quality metrics have regressed. "
            "Review the comparison table."
        )

    else:

        st.info(
            "No changes in data quality metrics compared with "
            "the previous execution."
        )

except (FileNotFoundError, ValueError) as error:

    st.info(str(error))

# ============================================================
# 12. DATA QUALITY RECOMMENDATIONS
# ============================================================

st.header("12. Data Quality Recommendations")

if "pipeline_results" not in st.session_state:
    st.info(
        "Run the data quality pipeline to generate recommendations."
    )

else:
    recommendation_results = (
        st.session_state["pipeline_results"].get(
            "recommendations",
            []
        )
    )

    if not recommendation_results:
        st.success(
            "No data quality recommendations. "
            "Your dataset has no detected issues requiring action."
        )

    else:
        high_count = sum(
            item["priority"] == "High"
            for item in recommendation_results
        )

        medium_count = sum(
            item["priority"] == "Medium"
            for item in recommendation_results
        )

        low_count = sum(
            item["priority"] == "Low"
            for item in recommendation_results
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Recommendations",
            len(recommendation_results)
        )

        col2.metric("High Priority", high_count)
        col3.metric("Medium Priority", medium_count)
        col4.metric("Low Priority", low_count)
        st.subheader("Recommended Actions")

        # Recommendation filters
        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:
            selected_priorities = st.multiselect(
                "Filter by Priority",
                options=["High", "Medium", "Low"],
                default=["High", "Medium", "Low"],
                key="recommendation_priority_filter"
            )

        with filter_col2:
            available_categories = sorted({
                item["category"]
                for item in recommendation_results
            })

            selected_categories = st.multiselect(
                "Filter by Category",
                options=available_categories,
                default=available_categories,
                key="recommendation_category_filter"
            )
                    # Search recommendations by keyword
        search_query = st.text_input(
            "Search Recommendations",
            placeholder="Search by issue, action, or category...",
            key="recommendation_search"
        ).strip().lower()
                # Sort recommendations
        sort_option = st.selectbox(
            "Sort Recommendations By",
            options=[
                "Priority (High to Low)",
                "Most Affected Records",
                "Least Affected Records",
                "Category (A to Z)"
            ],
            key="recommendation_sort"
        )
                # Apply priority, category, and keyword filters
        filtered_recommendations = [
            item
            for item in recommendation_results
            if item["priority"] in selected_priorities
            and item["category"] in selected_categories
            and (
                not search_query
                or search_query in str(item["category"]).lower()
                or search_query in str(item["priority"]).lower()
                or search_query in str(item["issue"]).lower()
                or search_query in str(item["recommendation"]).lower()
            )
        ]
                # Apply selected sorting option
        if sort_option == "Priority (High to Low)":
            priority_order = {
                "High": 0,
                "Medium": 1,
                "Low": 2
            }

            filtered_recommendations = sorted(
                filtered_recommendations,
                key=lambda item: priority_order.get(
                    item["priority"],
                    3
                )
            )

        elif sort_option == "Most Affected Records":
            filtered_recommendations = sorted(
                filtered_recommendations,
                key=lambda item: item["affected_count"],
                reverse=True
            )

        elif sort_option == "Least Affected Records":
            filtered_recommendations = sorted(
                filtered_recommendations,
                key=lambda item: item["affected_count"]
            )

        elif sort_option == "Category (A to Z)":
            filtered_recommendations = sorted(
                filtered_recommendations,
                key=lambda item: item["category"].lower()
            )
                    # Recommendation category analytics
        st.subheader("Recommendation Category Analysis")

        if filtered_recommendations:
            category_counts = (
                pd.DataFrame(filtered_recommendations)
                ["category"]
                .value_counts()
                .sort_index()
            )

            st.bar_chart(category_counts)

        else:
            st.info(
                "No recommendation data available for the chart."
            )

        st.write(
            f"Showing {len(filtered_recommendations)} "
            f"of {len(recommendation_results)} recommendations"
        )
        if not filtered_recommendations:
            st.info(
                "No recommendations match the selected filters. "
                "Try changing your priority or category selection."
            )

        recommendations_df = pd.DataFrame(
            filtered_recommendations
        )

        recommendations_df = recommendations_df.rename(
            columns={
                "category": "Category",
                "priority": "Priority",
                "issue": "Issue",
                "recommendation": "Recommended Action",
                "affected_count": "Affected Records"
            }
        )
        st.dataframe(
            recommendations_df,
            use_container_width=True,
            hide_index=True
        )

        # Export recommendations as CSV
        recommendations_csv = recommendations_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Recommendations (CSV)",
            data=recommendations_csv,
            file_name="data_quality_recommendations.csv",
            mime="text/csv",
            key="download_recommendations"
        )

        st.subheader("Detailed Recommendations")
        for index, item in enumerate(
            filtered_recommendations,
            start=1
        ):
            with st.expander(
                f"{index}. [{item['priority']}] {item['issue']}"
            ):
                st.write(
                    "**Category:**",
                    item["category"]
                )

                st.write(
                    "**Affected Records:**",
                    item["affected_count"]
                )

                st.write(
                    "**Recommended Action:**",
                    item["recommendation"]
                )
