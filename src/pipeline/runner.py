
import pandas as pd

from src.cleaning.clean import clean_dataframe
from src.validation.rules import validate_dataframe
from src.profiling.profile import profile_dataframe
from src.anomaly_detection.detect import detect_anomalies
from src.duplicate_detection.detect import detect_fuzzy_duplicates
from src.data_drift.detect import detect_data_drift
from src.reporting.html_report import generate_html_report
from src.history.history_tracker import save_quality_history
from src.utils.logger import get_logger


logger = get_logger("data_quality_pipeline")


def run_pipeline(df, reference_df=None):
    """
    Run the complete data quality pipeline.

    Args:
        df: Input pandas DataFrame.
        reference_df: Optional reference DataFrame for drift detection.

    Returns:
        Dictionary containing all pipeline results.
    """

    logger.info("Starting data quality pipeline")

    # Validate input
    if not isinstance(df, pd.DataFrame):
        logger.error("Invalid input: Expected a pandas DataFrame")
        raise TypeError("Input must be a pandas DataFrame")

    if df.empty:
        logger.error("Invalid input: DataFrame is empty")
        raise ValueError("Input DataFrame cannot be empty")

    logger.info("Input dataset validated. Shape: %s", df.shape)

    try:
        # Step 1: Clean the dataset
        logger.info("Step 1: Starting data cleaning")

        cleaned_df = clean_dataframe(df.copy())

        logger.info(
            "Step 1 completed. Cleaned dataset shape: %s",
            cleaned_df.shape
        )

        # Step 2: Validate the cleaned dataset
        logger.info("Step 2: Starting data validation")

        validation_issues = validate_dataframe(cleaned_df)

        logger.info(
            "Step 2 completed. Validation issues: %d",
            len(validation_issues)
        )

        # Step 3: Generate profiling report
        logger.info("Step 3: Starting data profiling")

        profiling_report = profile_dataframe(
            cleaned_df,
            file_name="pipeline_dataset.csv",
            verbose=False
        )

        logger.info("Step 3 completed. Profiling report generated")

        # Step 4: Detect anomalies
        logger.info("Step 4: Starting anomaly detection")

        anomaly_results = detect_anomalies(cleaned_df)

        anomaly_count = int(
            (anomaly_results["Anomaly"] == "Anomaly").sum()
        )

        logger.info(
            "Step 4 completed. Anomalies detected: %d",
            anomaly_count
        )

        # Step 5: Detect fuzzy duplicates
        logger.info("Step 5: Starting fuzzy duplicate detection")

        duplicate_results = detect_fuzzy_duplicates(cleaned_df)

        logger.info(
            "Step 5 completed. Fuzzy duplicate pairs: %d",
            len(duplicate_results)
        )

        # Step 6: Detect optional data drift
        drift_results = []

        if reference_df is not None:
            logger.info("Step 6: Starting data drift detection")

            drift_results = detect_data_drift(
                reference_df,
                cleaned_df
            )

            logger.info(
                "Step 6 completed. Drift results: %d",
                len(drift_results)
            )

        else:
            logger.info(
                "Step 6 skipped. No reference dataset provided"
            )

        # Step 7: Generate HTML report
        logger.info("Step 7: Starting HTML report generation")

        html_report_path = generate_html_report(
            profiling_report,
            validation_issues
        )

        logger.info(
            "Step 7 completed. HTML report generated: %s",
            html_report_path
        )

        # Step 8: Save quality history
        logger.info("Step 8: Saving quality history")

        history_path = save_quality_history(
            profiling_report,
            validation_issues,
            anomaly_results
        )

        logger.info(
            "Step 8 completed. Quality history saved: %s",
            history_path
        )

        # Collect all results
        results = {
            "cleaned_data": cleaned_df,
            "validation_issues": validation_issues,
            "profiling_report": profiling_report,
            "anomaly_results": anomaly_results,
            "duplicate_results": duplicate_results,
            "drift_results": drift_results,
            "html_report_path": html_report_path,
            "history_path": history_path
        }

        logger.info("Data quality pipeline completed successfully")

        return results

    except Exception:
        logger.exception("Data quality pipeline failed")
        raise
