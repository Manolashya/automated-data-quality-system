
import argparse
import sys
from pathlib import Path

import pandas as pd

from src.pipeline.runner import run_pipeline
from src.utils.logger import get_logger


logger = get_logger("data_quality_pipeline")


def report_error(message):
    """Display and record a CLI error."""
    logger.error(message)
    print(f"ERROR: {message}")
    sys.exit(1)


def main():

    parser = argparse.ArgumentParser(
        description="Automated Data Quality Pipeline CLI"
    )

    parser.add_argument(
        "input_file",
        help="Path to the input CSV dataset"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="data/processed/cleaned_data.csv",
        help="Path where the cleaned dataset will be saved"
    )

    parser.add_argument(
        "--reference",
        help="Optional reference CSV file for data drift detection"
    )

    args = parser.parse_args()

    input_path = Path(args.input_file)
    output_path = Path(args.output)

    # Check input dataset
    if not input_path.exists():
        report_error(f"Input file not found: {input_path}")

    if not input_path.is_file():
        report_error(f"Input path is not a file: {input_path}")

    if input_path.suffix.lower() != ".csv":
        report_error("Input file must be a CSV file.")

    # Load input dataset
    try:
        df = pd.read_csv(input_path)

        if df.empty:
            report_error("Input dataset is empty.")

        logger.info(
            "CLI loaded input dataset: %s | Shape: %s",
            input_path,
            df.shape
        )

        print("\nDATASET LOADED SUCCESSFULLY")
        print("----------------------------------------")
        print("Input file:", input_path)
        print("Original shape:", df.shape)

    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        report_error(f"Could not read input dataset: {error}")

    # Load optional reference dataset
    reference_df = None

    if args.reference:

        reference_path = Path(args.reference)

        if not reference_path.exists() or not reference_path.is_file():
            report_error(
                f"Reference file not found: {reference_path}"
            )

        if reference_path.suffix.lower() != ".csv":
            report_error("Reference file must be a CSV file.")

        try:
            reference_df = pd.read_csv(reference_path)

            if reference_df.empty:
                report_error("Reference dataset is empty.")

            logger.info(
                "CLI loaded reference dataset: %s | Shape: %s",
                reference_path,
                reference_df.shape
            )

            print("Reference file:", reference_path)
            print("Reference shape:", reference_df.shape)

        except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
            report_error(
                f"Could not read reference dataset: {error}"
            )

    # Execute pipeline
    try:

        print("\nRUNNING DATA QUALITY PIPELINE")
        print("----------------------------------------")

        results = run_pipeline(
            df,
            reference_df=reference_df
        )

        cleaned_df = results["cleaned_data"]

        # Save cleaned dataset
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        cleaned_df.to_csv(
            output_path,
            index=False
        )

        logger.info(
            "CLI saved cleaned dataset: %s",
            output_path.resolve()
        )

        # Display pipeline summary
        validation_issues = results["validation_issues"]
        anomaly_results = results["anomaly_results"]

        anomaly_count = int(
            (anomaly_results["Anomaly"] == "Anomaly").sum()
        )

        duplicate_results = results["duplicate_results"]
        drift_results = results["drift_results"]

        print("\nPIPELINE EXECUTION COMPLETED")
        print("----------------------------------------")

        print("Original rows:", len(df))
        print("Cleaned rows:", len(cleaned_df))
        print("Validation issues:", len(validation_issues))
        print("Anomalies detected:", anomaly_count)
        print("Fuzzy duplicate pairs:", len(duplicate_results))
        print("Data drift results:", len(drift_results))

        print("\nCLEANED DATASET SAVED SUCCESSFULLY")
        print("Output:", output_path.resolve())

        # Display validation issues
        if validation_issues:

            print("\nVALIDATION ISSUES")
            print("----------------------------------------")

            for issue in validation_issues:
                print(
                    f"Row: {issue['row_index']} | "
                    f"Column: {issue['column']} | "
                    f"Rule: {issue['rule']} | "
                    f"Message: {issue['message']}"
                )

        else:
            print("\nNo validation issues found.")

        # Display anomaly results
        if anomaly_count > 0:

            print("\nANOMALOUS RECORDS")
            print("----------------------------------------")

            print(
                anomaly_results[
                    anomaly_results["Anomaly"] == "Anomaly"
                ].to_string(index=False)
            )

        else:
            print("\nNo anomalies detected.")

        # Display fuzzy duplicate results
        if duplicate_results:

            print("\nFUZZY DUPLICATES")
            print("----------------------------------------")

            for duplicate in duplicate_results:
                print(duplicate)

        else:
            print("\nNo fuzzy duplicate pairs detected.")

        # Display data drift results
        if reference_df is not None:

            print("\nDATA DRIFT RESULTS")
            print("----------------------------------------")

            if drift_results:
                for drift in drift_results:
                    print(drift)
            else:
                print("No data drift results reported.")

        else:
            print("\nData drift analysis was skipped.")
            print("Provide --reference to perform data drift analysis.")

    except Exception as error:
        logger.error(
            "CLI pipeline execution failed: %s",
            error
        )
        print(f"\nERROR: Pipeline execution failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
