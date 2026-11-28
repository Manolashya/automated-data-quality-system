
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
from src.alerts.quality_alerts import generate_quality_alerts
from src.alerts.alert_history import load_alert_history
from src.utils.config_loader import load_config
from src.utils.threshold_validator import validate_quality_thresholds
from src.alerts.alert_analytics import analyze_alert_history
from src.alerts.alert_insights import generate_alert_insights
from src.history.trend_analyzer import analyze_quality_trends
from src.history.risk_assessor import assess_quality_risk
from src.history.risk_history import load_risk_history
from src.history.risk_trend_analyzer import analyze_risk_trends
from src.history.risk_comparator import compare_dataset_risks

from src.history.mitigation_tracker import (
    load_mitigation_actions,
    update_mitigation_status,
    VALID_STATUSES,
)


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
                # Explain overall quality score
        st.subheader("Quality Score Explanation")

        explanation = report.get(
            "quality_score_explanation", {}
        )

        if explanation:
            st.write(
                "**Formula:**",
                explanation.get("formula", "Not available")
            )

            st.write(
                "**Calculation:**",
                explanation.get("calculation", "Not available")
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Included Metrics",
                    explanation.get("included_metric_count", 0)
                )

            with col2:
                st.metric(
                    "Excluded Metrics",
                    explanation.get("excluded_metric_count", 0)
                )

            st.write("**Metrics included in the score:**")

            included_metrics = explanation.get(
                "included_metrics", {}
            )

            if included_metrics:
                included_df = pd.DataFrame(
                    list(included_metrics.items()),
                    columns=["Metric", "Score"]
                )

                st.dataframe(
                    included_df,
                    width="stretch",
                    hide_index=True
                )

            st.write("**Metrics excluded from the score:**")

            excluded_metrics = explanation.get(
                "excluded_metrics", []
            )

            if excluded_metrics:
                st.write(excluded_metrics)
            else:
                st.info("No metrics were excluded.")

        else:
            st.info(
                "Quality score explanation is not available. "
                "Run the profiling pipeline again."
            )

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
    reference_df=reference_df,
    dataset_name=dataset_name
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
                                # Dataset-wise quality comparison
                st.subheader("Dataset Quality Comparison")

                latest_dataset_history = (
                    valid_history
                    .sort_values("parsed_timestamp")
                    .groupby("dataset_name", as_index=False)
                    .tail(1)
                    .sort_values(
                        "quality_score",
                        ascending=False
                    )
                )

                comparison_columns = [
                    "dataset_name",
                    "quality_score",
                    "completeness",
                    "missing_values",
                    "duplicate_rows",
                    "validation_issues",
                    "anomalies"
                ]

                comparison_df = latest_dataset_history[
                    comparison_columns
                ].copy()

                st.bar_chart(
                    comparison_df.set_index("dataset_name")[
                        ["quality_score"]
                    ],
                    width="stretch"
                )

                st.dataframe(
                    comparison_df,
                    width="stretch",
                    hide_index=True
                )
                                # Compare additional quality metrics
                st.subheader("Quality Metrics Comparison")

                metrics_comparison = comparison_df.set_index(
                    "dataset_name"
                )[
                    [
                        "completeness",
                        "missing_values",
                        "duplicate_rows",
                        "validation_issues",
                        "anomalies"
                    ]
                ]

                st.bar_chart(
                    metrics_comparison,
                    width="stretch"
                )

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
                                # Automated Quality Trend Analysis
                st.subheader("Automated Quality Trend Analysis")

                # Analyze one dataset at a time
                trend_dataset = (
                    selected_dataset
                    if selected_dataset != "All Datasets"
                    else latest_record["dataset_name"]
                )

                trend_result = analyze_quality_trends(
                    valid_history,
                    dataset_name=trend_dataset
                )

                st.caption(
                    f"Trend analysis for: {trend_dataset}"
                )

                trend_col1, trend_col2, trend_col3 = st.columns(3)

                trend_col1.metric(
                    "Quality Trend",
                    trend_result["trend"]
                )

                trend_col2.metric(
                    "Latest Score",
                    (
                        f"{trend_result['latest_score']:.2f}%"
                        if trend_result["latest_score"] is not None
                        else "N/A"
                    )
                )

                trend_col3.metric(
                    "Change vs Previous",
                    (
                        f"{trend_result['score_change']:+.2f}%"
                        if trend_result["score_change"] is not None
                        else "N/A"
                    )
                )

                # Display trend status
                if trend_result["trend"] == "Improving":
                    st.success(
                        "Quality is improving compared with the previous execution."
                    )

                elif trend_result["trend"] == "Declining":
                    st.error(
                        "Quality is declining. Investigate the recent quality issues."
                    )

                elif trend_result["trend"] == "Stable":
                    st.info(
                        "Quality is stable compared with the previous execution."
                    )

                else:
                    st.info(
                        "More executions are needed to determine a quality trend."
                    )

                # Display recurring quality problems
                st.markdown("**Recurring Quality Problems**")

                issue_labels = {
                    "missing_values": "Missing Values",
                    "duplicate_rows": "Duplicate Rows",
                    "validation_issues": "Validation Issues",
                    "anomalies": "Anomalies"
                }

                if trend_result["recurring_issues"]:
                    for issue in trend_result["recurring_issues"]:
                        st.warning(
                            f"Recurring issue: {issue_labels.get(issue, issue)}"
                        )
                else:
                    st.success(
                        "No recurring quality problems detected."
                    )

                # Display automated trend warnings
                if trend_result["warnings"]:
                    st.markdown("**Trend Monitoring Warnings**")

                    for warning in trend_result["warnings"]:
                        st.write(f"- {warning}")

                st.caption(
                    f"Executions analyzed: {trend_result['execution_count']}"
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
        # Visualize improvement status
    st.subheader("Metric Improvement Status")

    improvement_status = pd.DataFrame(
        {
            "Metric Count": [
                improved_count,
                regressed_count,
                unchanged_count
            ]
        },
        index=[
            "Improved",
            "Regressed",
            "Unchanged"
        ]
    )

    st.bar_chart(
        improvement_status,
        width="stretch"
    )
        # Export quality improvement report
    improvement_report = comparison_display.copy()

    summary_rows = pd.DataFrame([
        {
            "Metric": "Improved Metrics",
            "Previous": None,
            "Latest": improved_count,
            "Difference": None,
            "Status": "Summary"
        },
        {
            "Metric": "Regressed Metrics",
            "Previous": None,
            "Latest": regressed_count,
            "Difference": None,
            "Status": "Summary"
        },
        {
            "Metric": "Unchanged Metrics",
            "Previous": None,
            "Latest": unchanged_count,
            "Difference": None,
            "Status": "Summary"
        }
    ])

    improvement_report = pd.concat(
        [improvement_report, summary_rows],
        ignore_index=True
    )

    improvement_csv = improvement_report.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Quality Improvement Report (CSV)",
        data=improvement_csv,
        file_name="quality_improvement_report.csv",
        mime="text/csv",
        key="download_quality_improvement_report"
    )

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

# ============================================================
# 13. Automated Quality Alerts
# ============================================================

st.header("13. Automated Quality Alerts")

st.write(
    "Monitor dataset quality against configured thresholds "
    "and identify critical issues and warnings automatically."
)

alert_report = None
alert_source = None

# Prefer the latest pipeline report for the selected dataset.
if (
    "pipeline_results" in st.session_state
    and st.session_state.get("pipeline_dataset_name") == dataset_name
):
    alert_report = st.session_state["pipeline_results"].get(
        "profiling_report"
    )
    alert_source = "Latest pipeline execution"

# Otherwise, use the saved report for the default dataset.
elif using_default_dataset and PROFILE_REPORT.exists():
    try:
        with open(PROFILE_REPORT, "r", encoding="utf-8") as file:
            alert_report = json.load(file)

        alert_source = "Saved project profiling report"

    except (OSError, json.JSONDecodeError) as error:
        st.error(f"Could not load the profiling report: {error}")

if alert_report is None:
    st.info(
        "No profiling report is available for the selected dataset. "
        "Run the Integrated Data Quality Pipeline to generate "
        "quality alerts."
    )

elif not isinstance(alert_report, dict):
    st.error("The profiling report has an invalid format.")

else:
    try:
        # Load and validate configured quality thresholds.
        threshold_config = load_config(
            PROJECT_ROOT / "config" / "quality_thresholds.yaml"
        )

        thresholds = validate_quality_thresholds(
            threshold_config
        )

        # Generate alerts using the existing alert engine.
        alerts = generate_quality_alerts(
            alert_report,
            thresholds
        )

        st.caption(f"Alert source: {alert_source}")

        # Display configured limits.
        st.subheader("Configured Quality Thresholds")

        threshold_col1, threshold_col2, threshold_col3 = (
            st.columns(3)
        )

        threshold_col1.metric(
            "Minimum Quality Score",
            f"{thresholds['minimum_overall_score']:.2f}%"
        )

        threshold_col2.metric(
            "Maximum Missing Values",
            f"{thresholds['maximum_missing_percentage']:.2f}%"
        )

        threshold_col3.metric(
            "Maximum Duplicate Rows",
            f"{thresholds['maximum_duplicate_percentage']:.2f}%"
        )

        # Display alert summary.
        st.subheader("Alert Summary")

        critical_count = sum(
            alert["severity"] == "Critical"
            for alert in alerts
        )

        warning_count = sum(
            alert["severity"] == "Warning"
            for alert in alerts
        )

        total_alerts = len(alerts)

        summary_col1, summary_col2, summary_col3 = (
            st.columns(3)
        )

        summary_col1.metric(
            "Total Alerts",
            total_alerts
        )

        summary_col2.metric(
            "Critical Alerts",
            critical_count
        )

        summary_col3.metric(
            "Warning Alerts",
            warning_count
        )

        # Display detailed alerts.
        st.subheader("Alert Details")

        if alerts:
            alert_df = pd.DataFrame(alerts)

            st.dataframe(
                alert_df[
                    [
                        "metric",
                        "actual_value",
                        "threshold",
                        "severity",
                        "message",
                    ]
                ],
                width="stretch",
                hide_index=True
            )

            for alert in alerts:
                alert_message = (
                    f"**{alert['metric']}** — "
                    f"Actual: {alert['actual_value']} | "
                    f"Threshold: {alert['threshold']}"
                )

                if alert["severity"] == "Critical":
                    st.error(
                        f"{alert_message}\n\n"
                        f"{alert['message']}"
                    )

                else:
                    st.warning(
                        f"{alert_message}\n\n"
                        f"{alert['message']}"
                    )

        else:
            st.success(
                "No quality alerts detected! "
                "All monitored metrics meet the configured thresholds."
            )

    except (ValueError, KeyError, TypeError, OSError) as error:
        st.error(
            f"Could not generate quality alerts: {error}"
        )
# ============================================================
# 14. Quality Alert History
# ============================================================

st.header("14. Quality Alert History")

st.write(
    "View previously generated quality alerts, including "
    "their timestamps, dataset names, severity, and messages."
)

try:
    alert_history = load_alert_history()

    if alert_history:
        history_df = pd.DataFrame(alert_history)

        # Display the newest alert records first.
        history_df = history_df.sort_values(
            by="timestamp",
            ascending=False
        )

        st.metric(
            "Total Historical Alert Records",
            len(history_df)
        )

        st.dataframe(
            history_df[
                [
                    "timestamp",
                    "dataset_name",
                    "metric",
                    "actual_value",
                    "threshold",
                    "severity",
                    "message",
                ]
            ],
            width="stretch",
            hide_index=True
        )

    else:
        st.info(
            "No historical quality alerts are available yet. "
            "Alert records will appear here after a pipeline "
            "execution generates quality alerts."
        )

except (OSError, ValueError, KeyError) as error:
    st.error(
        f"Could not load quality alert history: {error}"
    )
# ---------------------------------------------------------
# 15. HISTORICAL ALERT ANALYTICS
# ---------------------------------------------------------

st.header("Historical Alert Analytics")

alert_history = load_alert_history()

if alert_history:
    analytics = analyze_alert_history(alert_history)

    # Total alerts
    st.metric(
        "Total Historical Alerts",
        analytics["total_alerts"]
    )

    # Severity analysis
    st.subheader("Alert Severity Analysis")

    severity_data = pd.DataFrame.from_dict(
        analytics["severity_counts"],
        orient="index",
        columns=["Alerts"]
    )

    st.bar_chart(severity_data)

    # Metric analysis
    st.subheader("Most Frequently Affected Metrics")

    metric_data = pd.DataFrame.from_dict(
        analytics["metric_counts"],
        orient="index",
        columns=["Alerts"]
    )

    st.bar_chart(metric_data)

    # Dataset analysis
    st.subheader("Datasets with Most Alerts")

    dataset_data = pd.DataFrame.from_dict(
        analytics["dataset_counts"],
        orient="index",
        columns=["Alerts"]
    )

    st.bar_chart(dataset_data)

    # Daily alert trends
    st.subheader("Daily Alert Trends")

    daily_counts = {
        date: count
        for date, count in analytics["daily_counts"].items()
        if date != "Unknown"
    }

    if daily_counts:
        daily_data = pd.DataFrame.from_dict(
            daily_counts,
            orient="index",
            columns=["Alerts"]
        )

        st.line_chart(daily_data)
    else:
        st.info("No valid dates available for daily trend analysis.")

else:
    st.info("No historical alert data available for analytics.")

# ---------------------------------------------------------
# 16. QUALITY ALERT INSIGHTS & RECOMMENDATIONS
# ---------------------------------------------------------

st.header("Quality Alert Insights & Recommendations")

alert_history = load_alert_history()

if alert_history:
    insights = generate_alert_insights(alert_history)

    if insights:
        for insight in insights:
            with st.container(border=True):
                st.subheader(insight["title"])

                priority = insight["priority"]

                if priority == "High":
                    st.error(f"Priority: {priority}")
                elif priority == "Medium":
                    st.warning(f"Priority: {priority}")
                else:
                    st.info(f"Priority: {priority}")

                st.write("**Finding:**")
                st.write(insight["finding"])

                st.write("**Recommended Action:**")
                st.write(insight["recommendation"])
    else:
        st.success("No significant alert insights found.")

else:
    st.info(
        "No historical alert data available. "
        "Run the quality pipeline to generate alert insights."
    )


# ---------------------------------------------------------
# 17. AUTOMATED QUALITY RISK ASSESSMENT
# ---------------------------------------------------------

st.header("17. Automated Quality Risk Assessment")

st.write(
    "Assess current dataset quality risks using configured thresholds "
    "and historical quality trends."
)

st.caption(
    "This is an explainable, rule-based early-warning assessment, "
    "not a trained machine-learning prediction."
)

risk_history_path = PROJECT_ROOT / "reports" / "quality_history.csv"

if not risk_history_path.exists():

    st.info(
        "No quality history is available. Run the quality pipeline "
        "to generate records before assessing risk."
    )

else:

    try:
        risk_history = pd.read_csv(risk_history_path)

        required_risk_columns = [
            "timestamp",
            "dataset_name",
            "rows",
            "columns",
            "quality_score",
            "missing_values",
            "duplicate_rows",
        ]

        missing_risk_columns = [
            column
            for column in required_risk_columns
            if column not in risk_history.columns
        ]

        if missing_risk_columns:
            st.warning(
                f"Quality history is missing required columns: "
                f"{missing_risk_columns}"
            )

        elif risk_history.empty:
            st.info("The quality history file contains no records.")

        else:
            risk_history["parsed_timestamp"] = pd.to_datetime(
                risk_history["timestamp"],
                errors="coerce",
                utc=True
            )

            risk_history["quality_score"] = pd.to_numeric(
                risk_history["quality_score"],
                errors="coerce"
            )

            valid_risk_history = risk_history.dropna(
                subset=["parsed_timestamp", "quality_score", "dataset_name"]
            ).sort_values("parsed_timestamp")

            if valid_risk_history.empty:
                st.info("No valid quality history records are available.")

            else:
                # Reuse the dataset selected in Section 10.
                chosen_risk_dataset = st.session_state.get(
                    "quality_history_dataset_filter",
                    "All Datasets"
                )

                available_risk_datasets = (
                    valid_risk_history["dataset_name"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

                if chosen_risk_dataset not in available_risk_datasets:
                    chosen_risk_dataset = "All Datasets"

                if chosen_risk_dataset == "All Datasets":
                    risk_dataset = valid_risk_history.iloc[-1][
                        "dataset_name"
                    ]
                else:
                    risk_dataset = chosen_risk_dataset

                dataset_risk_history = valid_risk_history[
                    valid_risk_history["dataset_name"] == risk_dataset
                ].copy()

                latest_risk_record = dataset_risk_history.iloc[-1]

                # Build the profiling summary from the matching
                # dataset's latest historical execution.
                risk_profiling_report = {
                    "file_name": str(risk_dataset),
                    "rows": int(latest_risk_record["rows"]),
                    "column_count": int(latest_risk_record["columns"]),
                    "overall_quality_score": float(
                        latest_risk_record["quality_score"]
                    ),
                    "missing_values": int(
                        pd.to_numeric(
                            latest_risk_record["missing_values"],
                            errors="coerce"
                        )
                    ),
                    "duplicate_rows": int(
                        pd.to_numeric(
                            latest_risk_record["duplicate_rows"],
                            errors="coerce"
                        )
                    ),
                }

                # Load the same configured thresholds used by
                # the existing quality alert system.
                risk_threshold_config = load_config(
                    PROJECT_ROOT / "config" / "quality_thresholds.yaml"
                )

                risk_thresholds = validate_quality_thresholds(
                    risk_threshold_config
                )

                risk_result = assess_quality_risk(
                    profiling_report=risk_profiling_report,
                    history=dataset_risk_history,
                    thresholds=risk_thresholds,
                    dataset_name=str(risk_dataset),
                )

                st.subheader("Current Risk Assessment")

                st.caption(f"Dataset assessed: {risk_result['dataset_name']}")

                risk_col1, risk_col2, risk_col3 = st.columns(3)

                risk_col1.metric(
                    "Risk Score",
                    f"{risk_result['risk_score']:.2f} / 100"
                )

                risk_col2.metric(
                    "Risk Level",
                    risk_result["risk_level"]
                )

                risk_col3.metric(
                    "Quality Trend",
                    risk_result["trend"]
                )

                st.progress(
                    risk_result["risk_score"] / 100
                )

                if risk_result["risk_level"] == "Critical":
                    st.error("Critical quality risk detected.")

                elif risk_result["risk_level"] == "High":
                    st.error("High quality risk detected.")

                elif risk_result["risk_level"] == "Medium":
                    st.warning("Moderate quality risk detected.")

                else:
                    st.success("Low quality risk detected.")

                st.subheader("Risk Indicators")

                indicator_col1, indicator_col2 = st.columns(2)

                indicator_col1.metric(
                    "Missing Values",
                    f"{risk_result['missing_percentage']:.2f}%"
                )

                indicator_col2.metric(
                    "Duplicate Rows",
                    f"{risk_result['duplicate_percentage']:.2f}%"
                )

                st.subheader("Risk Contributing Factors")

                if risk_result["factors"]:
                    factors_df = pd.DataFrame(
                        risk_result["factors"]
                    )

                    st.dataframe(
                        factors_df,
                        width="stretch",
                        hide_index=True
                    )
                else:
                    st.info("No risk-contributing factors were detected.")

                st.subheader("Early Warnings")

                for warning in risk_result["warnings"]:
                    st.warning(warning)

                st.subheader("Recommended Actions")

                for index, recommendation in enumerate(
                    risk_result["recommendations"],
                    start=1
                ):
                    st.write(f"{index}. {recommendation}")

                st.caption(
                    f"Historical executions analyzed: "
                    f"{len(dataset_risk_history)}"
                )

    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        ZeroDivisionError,
    ) as error:
        st.error(
            f"Could not complete the quality risk assessment: {error}"
        )


# ---------------------------------------------------------
# 18. RISK HISTORY AND TREND ANALYSIS
# ---------------------------------------------------------

st.header("18. Risk History and Trend Analysis")

try:
    saved_risk_history = load_risk_history()

    if saved_risk_history.empty:
        st.info(
            "No saved risk history is available yet. "
            "Run the data quality pipeline to create risk history records."
        )

    else:
        required_columns = [
            "timestamp",
            "dataset_name",
            "risk_score",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in saved_risk_history.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Risk history is missing required columns: {missing_columns}"
            )

        risk_history_data = saved_risk_history.copy()

        risk_history_data["parsed_timestamp"] = pd.to_datetime(
            risk_history_data["timestamp"],
            errors="coerce",
            utc=True
        )

        risk_history_data["risk_score"] = pd.to_numeric(
            risk_history_data["risk_score"],
            errors="coerce"
        )

        risk_history_data = risk_history_data.dropna(
            subset=["parsed_timestamp", "risk_score", "dataset_name"]
        )

        risk_history_data = risk_history_data[
            risk_history_data["risk_score"].between(0, 100)
        ].sort_values("parsed_timestamp")

        if risk_history_data.empty:
            st.info("No valid risk history records were found.")

        else:
            selected_dataset = st.session_state.get(
                "quality_history_dataset_filter",
                "All Datasets"
            )

            available_datasets = (
                risk_history_data["dataset_name"]
                .astype(str)
                .unique()
                .tolist()
            )

            if selected_dataset == "All Datasets":
                risk_dataset = risk_history_data.iloc[-1]["dataset_name"]
                st.caption(
                    "Showing the most recently recorded dataset because "
                    "the dataset filter is set to All Datasets."
                )

            elif selected_dataset in available_datasets:
                risk_dataset = selected_dataset

            else:
                st.info(
                    f"No saved risk history is available for "
                    f"'{selected_dataset}'. Run the pipeline for this dataset "
                    "to create its risk history."
                )
                risk_dataset = None

            if risk_dataset is not None:
                dataset_risk_history = risk_history_data[
                    risk_history_data["dataset_name"] == risk_dataset
                ].copy()

                trend_result = analyze_risk_trends(
                    dataset_risk_history,
                    dataset_name=str(risk_dataset)
                )

                latest_record = dataset_risk_history.iloc[-1]

                st.subheader("Latest Saved Risk Assessment")

                st.caption(f"Dataset: {risk_dataset}")

                history_col1, history_col2, history_col3 = st.columns(3)

                history_col1.metric(
                    "Latest Risk Score",
                    f"{float(latest_record['risk_score']):.2f} / 100"
                )

                if "risk_level" in latest_record.index:
                    history_col2.metric(
                        "Risk Level",
                        str(latest_record["risk_level"])
                    )
                else:
                    history_col2.metric("Risk Level", "Not available")

                history_col3.metric(
                    "Risk Trend",
                    trend_result["trend"]
                )

                if trend_result["score_change"] is not None:
                    st.metric(
                        "Change vs Previous Execution",
                        f"{trend_result['score_change']:+.2f}",
                        delta_color="inverse"
                    )
                else:
                    st.metric(
                        "Change vs Previous Execution",
                        "Insufficient data"
                    )

                st.caption(
                    f"Valid historical executions: "
                    f"{trend_result['execution_count']}"
                )

                for warning in trend_result["warnings"]:
                    if trend_result["trend"] == "Worsening":
                        st.warning(warning)
                    elif trend_result["trend"] == "Improving":
                        st.success(warning)
                    else:
                        st.info(warning)

                st.subheader("Risk Score History")

                chart_data = dataset_risk_history[
                    ["parsed_timestamp", "risk_score"]
                ].copy()

                chart_data = chart_data.set_index("parsed_timestamp")

                st.line_chart(
                    chart_data,
                    width="stretch"
                )

                st.subheader("Historical Risk Records")

                display_columns = [
                    column
                    for column in [
                        "timestamp",
                        "dataset_name",
                        "risk_score",
                        "risk_level",
                        "quality_score",
                        "missing_percentage",
                        "duplicate_percentage",
                        "trend",
                        "recurring_issues",
                    ]
                    if column in dataset_risk_history.columns
                ]

                display_history = dataset_risk_history.sort_values(
                    "parsed_timestamp",
                    ascending=False
                )

                st.dataframe(
                    display_history[display_columns],
                    width="stretch",
                    hide_index=True
                )

except (
    OSError,
    ValueError,
    TypeError,
    KeyError,
    ZeroDivisionError,
) as error:
    st.error(
        f"Could not load or analyze risk history: {error}"
    )

# --------------------------------------------------
# 19. Multi-Dataset Risk Comparison
# --------------------------------------------------

st.header("19. Multi-Dataset Risk Comparison")

try:
    comparison_history = load_risk_history()

    latest_risk_comparison = compare_dataset_risks(
        comparison_history
    )

    if latest_risk_comparison.empty:
        st.info(
            "No valid dataset risk records are available for comparison. "
            "Run the data quality pipeline for multiple datasets."
        )

    else:
        st.write(
            "This section compares the latest saved risk assessment "
            "for each dataset."
        )

        highest_risk = latest_risk_comparison.iloc[0]
        lowest_risk = latest_risk_comparison.iloc[-1]

        comparison_col1, comparison_col2, comparison_col3 = (
            st.columns(3)
        )

        comparison_col1.metric(
            "Datasets Compared",
            len(latest_risk_comparison)
        )

        comparison_col2.metric(
            "Highest Risk",
            f"{highest_risk['risk_score']:.2f} / 100",
            help=str(highest_risk["dataset_name"])
        )

        comparison_col3.metric(
            "Lowest Risk",
            f"{lowest_risk['risk_score']:.2f} / 100",
            help=str(lowest_risk["dataset_name"])
        )

        st.subheader("Risk Score Comparison")

        risk_chart = latest_risk_comparison[
            ["dataset_name", "risk_score"]
        ].copy()

        risk_chart = risk_chart.set_index("dataset_name")

        st.bar_chart(
            risk_chart,
            width="stretch"
        )

        st.subheader("Risk-Level Distribution")

        risk_order = [
            "Low",
            "Medium",
            "High",
            "Critical",
        ]

        risk_distribution = (
            latest_risk_comparison["risk_level"]
            .value_counts()
            .reindex(risk_order, fill_value=0)
            .rename_axis("Risk Level")
            .reset_index(name="Dataset Count")
        )

        st.bar_chart(
            risk_distribution.set_index("Risk Level"),
            width="stretch"
        )

        st.dataframe(
            risk_distribution,
            width="stretch",
            hide_index=True
        )

        st.subheader("Dataset Risk Comparison Table")

        comparison_columns = [
            "dataset_name",
            "risk_score",
            "risk_level",
            "timestamp",
        ]

        st.dataframe(
            latest_risk_comparison[comparison_columns],
            width="stretch",
            hide_index=True
        )

except (
    OSError,
    ValueError,
    TypeError,
    KeyError,
) as error:
    st.error(
        f"Could not compare dataset risks: {error}"
    )


# --------------------------------------------------
# 20. Risk Mitigation Action Tracking
# --------------------------------------------------

st.header("20. Risk Mitigation Action Tracking")

try:
    mitigation_actions = load_mitigation_actions()

    if mitigation_actions.empty:
        st.info(
            "No mitigation actions are available yet. "
            "Run the data quality pipeline to generate mitigation tasks."
        )

    else:
        st.write(
            "Track recommended actions generated from risk assessments. "
            "Update each task as work progresses."
        )

        total_actions = len(mitigation_actions)

        pending_count = int(
            (mitigation_actions["status"] == "Pending").sum()
        )

        in_progress_count = int(
            (mitigation_actions["status"] == "In Progress").sum()
        )

        completed_count = int(
            (mitigation_actions["status"] == "Completed").sum()
        )

        metric_col1, metric_col2, metric_col3, metric_col4 = (
            st.columns(4)
        )

        metric_col1.metric("Total Actions", total_actions)
        metric_col2.metric("Pending", pending_count)
        metric_col3.metric("In Progress", in_progress_count)
        metric_col4.metric("Completed", completed_count)

        completion_percentage = completed_count / total_actions

        st.subheader("Mitigation Completion Progress")

        st.progress(completion_percentage)

        st.caption(
            f"{completed_count} of {total_actions} actions completed "
            f"({completion_percentage * 100:.1f}%)"
        )

        st.subheader("Saved Mitigation Tasks")

        display_columns = [
            "dataset_name",
            "risk_level",
            "priority",
            "recommendation",
            "status",
            "created_at",
            "updated_at",
        ]

        st.dataframe(
            mitigation_actions[display_columns],
            width="stretch",
            hide_index=True,
        )

        st.subheader("Update Mitigation Task Status")

        action_options = (
            mitigation_actions["action_id"].astype(str).tolist()
        )

        action_labels = {}

        for _, action in mitigation_actions.iterrows():
            action_id = str(action["action_id"])

            action_labels[action_id] = (
                f"{action['dataset_name']} | "
                f"{action['priority']} | "
                f"{str(action['recommendation'])[:70]}"
            )

        selected_action_id = st.selectbox(
            "Select a mitigation task",
            options=action_options,
            format_func=action_labels.get,
            key="mitigation_action_selector",
        )

        selected_action = mitigation_actions[
            mitigation_actions["action_id"].astype(str)
            == selected_action_id
        ].iloc[0]

        current_status = str(selected_action["status"])

        if current_status not in VALID_STATUSES:
            st.error(
                f"Invalid saved status: {current_status}"
            )
        else:
            new_status = st.selectbox(
                "Select the new status",
                options=VALID_STATUSES,
                index=VALID_STATUSES.index(current_status),
                key="mitigation_status_selector",
            )

            if st.button(
                "Update Mitigation Status",
                key="update_mitigation_status",
            ):
                update_mitigation_status(
                    action_id=selected_action_id,
                    status=new_status,
                )

                st.success(
                    f"Task status updated to: {new_status}"
                )

                st.rerun()

except (
    OSError,
    ValueError,
    TypeError,
    KeyError,
    IndexError,
) as error:
    st.error(
        f"Could not load or update mitigation actions: {error}"
    )
