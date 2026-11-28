
import pandas as pd

from src.cleaning.clean import clean_dataframe
from src.validation.rules import validate_dataframe
from src.profiling.profile import profile_dataframe
from src.anomaly_detection.detect import detect_anomalies
from src.duplicate_detection.detect import detect_fuzzy_duplicates
from src.data_drift.detect import detect_data_drift
from src.reporting.html_report import generate_html_report
from src.history.history_tracker import save_quality_history
from src.history.risk_assessor import assess_quality_risk
from src.history.risk_history import save_risk_history
import src.history.mitigation_tracker as mitigation_tracker
from src.history.history_comparator import compare_quality_history
from src.recommendations.recommendation_engine import (
    generate_recommendations,
)
from src.utils.logger import get_logger
from pathlib import Path

from src.alerts.quality_alerts import generate_quality_alerts
from src.alerts.alert_history import save_alert_history
from src.utils.config_loader import load_config
from src.utils.threshold_validator import validate_quality_thresholds


logger = get_logger("data_quality_pipeline")


def run_pipeline(
    df,
    reference_df=None,
    dataset_name="pipeline_dataset.csv"
):
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

        # Step 9: Compare quality history when available
        logger.info("Step 9: Comparing quality history")

        history_comparison = None

        try:
            history_comparison = compare_quality_history(
                history_path
            )

            logger.info(
                "Step 9 completed. Historical comparison available"
            )

        except (FileNotFoundError, ValueError) as error:
            logger.info(
                "Step 9 skipped. Historical comparison unavailable: %s",
                error
            )

        # Step 10: Generate data quality recommendations
        logger.info("Step 10: Generating recommendations")

        recommendations = generate_recommendations(
            validation_issues=validation_issues,
            anomaly_results=anomaly_results,
            duplicate_results=duplicate_results,
            drift_results=drift_results,
            history_comparison=history_comparison,
        )

        logger.info(
            "Step 10 completed. Recommendations generated: %d",
            len(recommendations)
        )
        # Step 11: Generate and save quality alerts
        logger.info("Step 11: Generating quality alerts")

        project_root = Path(__file__).resolve().parents[2]

        threshold_config = load_config(
            project_root / "config" / "quality_thresholds.yaml"
        )

        thresholds = validate_quality_thresholds(
            threshold_config
        )

        alerts = generate_quality_alerts(
            profiling_report,
            thresholds
        )

        alert_history_path = save_alert_history(
            alerts,
            dataset_name
        )

        logger.info(
            "Step 11 completed. Alerts generated: %d",
            len(alerts)
        )

        # Step 12: Assess and save quality risk
        logger.info("Step 12: Assessing quality risk")

        quality_history = pd.read_csv(history_path)

        risk_result = assess_quality_risk(
            profiling_report=profiling_report,
            history=quality_history,
            thresholds=thresholds,
            dataset_name=profiling_report["file_name"],
        )

        risk_history_path = save_risk_history(risk_result)

        # Step 13: Generate and save risk mitigation actions
        logger.info("Step 13: Generating mitigation actions")

        mitigation_actions = (
            mitigation_tracker.generate_mitigation_actions(risk_result)
        )
        mitigation_actions_path = (
            mitigation_tracker.DEFAULT_MITIGATION_PATH
        )

        logger.info(
            "Step 13 completed. New mitigation actions: %d",
            len(mitigation_actions),
        )

        logger.info(
            "Step 12 completed. Risk score: %.2f (%s)",
            risk_result["risk_score"],
            risk_result["risk_level"],
        )

        # Collect all results
        results = {
            "cleaned_data": cleaned_df,
            "validation_issues": validation_issues,
            "profiling_report": profiling_report,
            "anomaly_results": anomaly_results,
            "duplicate_results": duplicate_results,
            "drift_results": drift_results,
            "recommendations": recommendations,
            "html_report_path": html_report_path,
            "history_path": history_path,
            "alerts": alerts,
            "alert_history_path": alert_history_path,
            "risk_result": risk_result,
            "risk_history_path": risk_history_path,
            "mitigation_actions": mitigation_actions,
            "mitigation_actions_path": mitigation_actions_path,
        }
        logger.info("Data quality pipeline completed successfully")

        return results

    except Exception:
        logger.exception("Data quality pipeline failed")
        raise
