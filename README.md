
# Automated Data Cleaning & Validation System

An end-to-end Python-based data quality system that profiles datasets, identifies data quality issues, cleans inconsistent data, validates records, detects anomalies, identifies potential duplicate records, monitors data drift, and generates structured reports.

- **Project:** CadetX — Hands-On Ecosystem for Junior Data Professionals
- **Repository:** [Manolashya/automated-data-quality-system](https://github.com/Manolashya/automated-data-quality-system)
- **Primary language:** Python
- **Development milestone:** Days 1-30 completed
- **Latest test result:** 90 tests passed, 93% code coverage

---

## 1. Project Overview

Real-world datasets often contain missing values, duplicate records, inconsistent formats, invalid entries, and unreliable data types. These problems can affect analysis, reporting, and downstream applications.

This project provides a modular data quality solution that combines traditional data processing techniques with machine-learning-based analysis.

### Key features

- Dataset profiling and metadata analysis
- Missing-value and duplicate detection
- Data cleaning and transformation
- Rule-based data quality validation
- Mean, median, and mode missing-value imputation
- Machine-learning-based anomaly detection using Isolation Forest
- Fuzzy duplicate detection using RapidFuzz
- Numerical and categorical data drift detection
- Automated end-to-end pipeline execution
- Command-line interface (CLI)
- Interactive Streamlit dashboard
- Structured logging and error handling
- Automated unit and integration testing
- JSON profiling report generation
- Cleaned dataset export

---

## 2. Project Objectives

1. Understand the structure and quality of raw datasets.
2. Identify missing values, duplicate records, and invalid entries.
3. Detect semantic column types and potential PII columns.
4. Clean inconsistent data while preserving original input data.
5. Validate customer data using predefined rules.
6. Generate structured profiling reports.
7. Apply suitable missing-value imputation strategies.
8. Detect anomalous records using machine learning.
9. Identify potentially duplicated records using fuzzy matching.
10. Detect changes in numerical and categorical data distributions.
11. Integrate individual modules into an automated pipeline.
12. Provide CLI and dashboard interfaces.
13. Improve reliability through logging, error handling, and automated tests.

---

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data loading, cleaning, and analysis |
| NumPy | Numerical operations |
| Scikit-learn | Isolation Forest anomaly detection |
| RapidFuzz | Fuzzy string matching |
| SciPy | Statistical and scientific operations |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualization |
| Streamlit | Interactive dashboard |
| PyYAML | YAML configuration support |
| JSON | Structured profiling reports |
| Pytest | Automated testing |
| pytest-cov | Test coverage measurement |
| Logging | Application logging and debugging |
| Git | Version control |
| GitHub | Source code hosting |

---

## 4. Project Architecture

```text
automated-data-quality-system/
|
|-- data/
|   |-- raw/
|   |   |-- customer_data.csv
|   |   |-- dirty_customer_data.csv
|   |
|   |-- processed/
|       |-- cleaned_data.csv
|
|-- dashboard/
|   |-- app.py
|
|-- src/
|   |-- profiling/
|   |   |-- profile.py
|   |   |-- profile_backup.py
|   |
|   |-- cleaning/
|   |   |-- clean.py
|   |   |-- cleaning_utils.py
|   |
|   |-- validation/
|   |   |-- rules.py
|   |
|   |-- anomaly_detection/
|   |   |-- detect.py
|   |
|   |-- duplicate_detection/
|   |   |-- detect.py
|   |
|   |-- data_drift/
|   |   |-- detect.py
|   |
|   |-- pipeline/
|   |   |-- runner.py
|   |   |-- cli.py
|   |
|   |-- utils/
|       |-- logger.py
|
|-- tests/
|   |-- test_anomaly_detection.py
|   |-- test_cleaned_dataset.py
|   |-- test_cleaning.py
|   |-- test_cli_integration.py
|   |-- test_data_drift.py
|   |-- test_duplicate_detection.py
|   |-- test_missing_values.py
|   |-- test_pipeline_integration.py
|   |-- test_profiling.py
|   |-- test_profiling_report.py
|   |-- test_validation_rules.py
|
|-- reports/
|   |-- profiling_report.json
|
|-- logs/
|   |-- pipeline.log
|
|-- requirements.txt
|-- README.md
|-- .gitignore
```

Generated files, temporary files, and Python cache directories may also be present locally.

---

## 5. Implemented Modules

### Module 1: Data Profiling and Metadata Analysis

Location: `src/profiling/profile.py`

The profiling module analyses a dataset and generates useful information about its structure and quality.

Implemented features:

- Dataset row and column counts
- Column names and data types
- Missing-value counts and percentages
- Duplicate-row counts
- Numerical statistical summaries
- Categorical value distributions
- Cardinality analysis
- Numerical correlation analysis
- Semantic column detection
- Email and phone pattern detection
- Mixed-type inspection
- Missing-value matrix
- Type consistency checks
- PII column identification
- Suspicious-column identification
- Overall data quality scoring

The profiler generates a structured JSON report at:

`reports/profiling_report.json`

### Module 2: Data Cleaning and Transformation

Location: `src/cleaning/clean.py`

Implemented cleaning operations:

- Whitespace normalization
- Gender standardization, including M/F representations
- Numeric conversion
- Missing-value handling for supported columns
- Email and phone validation support
- Invalid date identification
- Customer identifier and categorical-field checks
- Exact duplicate removal
- Saving cleaned data separately from raw data

The cleaned dataset is saved to:

`data/processed/cleaned_data.csv`

The original raw dataset is preserved.

### Module 3: Data Quality Validation

Location: `src/validation/rules.py`

The validation module checks customer records against predefined rules.

Validation areas include:

- Required columns and values
- Email format
- Phone number format
- Purchase date validity
- Age range
- Non-negative income
- Non-negative purchase amount
- Allowed gender values
- Allowed city values
- Customer ID format

Validation issues are returned as structured results containing information such as row index, column, rule, and message.

### Module 4: Missing-Value Imputation

Location: `src/cleaning/cleaning_utils.py`

Implemented strategies:

- Mean imputation for numerical columns
- Median imputation for selected numerical columns
- Mode imputation for categorical columns
- Handling of entirely missing columns
- Preservation of the original DataFrame

The imputation strategy can be selected according to the characteristics of the dataset.

### Module 5: Machine Learning-Based Anomaly Detection

Location: `src/anomaly_detection/detect.py`

Uses the Isolation Forest algorithm from Scikit-learn.

Implemented features:

- Detect unusual numerical observations
- Generate anomaly labels
- Generate anomaly scores
- Handle missing values
- Validate input data and contamination settings
- Preserve the original DataFrame

An anomaly represents a potentially unusual observation. It does not automatically mean that the record is incorrect or should be deleted.

### Module 6: Fuzzy Duplicate Detection

Location: `src/duplicate_detection/detect.py`

Uses RapidFuzz to identify potentially duplicated records based on string similarity.

Implemented features:

- Fuzzy string matching
- Similarity score calculation
- Configurable similarity threshold
- Case-insensitive matching
- Custom comparison-column support
- Missing and empty-value handling
- Matching row indexes and similarity scores
- Input validation

Example:

- Rahul Kumar
- Rahul Kmar

These names can be identified as potentially similar.

Fuzzy duplicate detection reports potential matches without automatically deleting records.

### Module 7: Data Drift Detection

Location: `src/data_drift/detect.py`

Compares a reference dataset with a current dataset to identify distribution changes.

**Numerical drift — Population Stability Index (PSI)**

- Numerical binning using reference dataset quantiles
- Distribution comparison
- Zero-frequency smoothing
- PSI score calculation
- Configurable drift threshold

**Categorical drift — Total Variation Distance (TVD)**

- Category proportion comparison
- Handling of categories present in only one dataset
- Missing-value handling
- TVD score calculation
- Configurable drift threshold

Additional handling:

- Input validation
- Configurable numerical bins
- Comparison of common columns
- Skipping columns without usable values
- Preservation of original datasets

Drift scores should be interpreted according to their statistical method and configured threshold.

### Module 8: Integrated Data Quality Pipeline

Location: `src/pipeline/runner.py`

The pipeline integrates the individual modules into one reusable workflow.

Implemented stages:

1. Input DataFrame validation
2. Data cleaning
3. Rule-based validation
4. Dataset profiling
5. Anomaly detection
6. Fuzzy duplicate detection
7. Optional data drift detection
8. Collection of pipeline results

The pipeline returns a dictionary containing:

- `cleaned_data`
- `validation_issues`
- `profiling_report`
- `anomaly_results`
- `duplicate_results`
- `drift_results`

An optional reference DataFrame can be provided to enable data drift detection.

### Module 9: Command-Line Interface

Location: `src/pipeline/cli.py`

The CLI allows users to execute the complete data quality pipeline from PowerShell or a terminal.

Implemented features:

- Input CSV selection
- Custom output path
- Optional reference dataset
- Input file validation
- CSV format validation
- Empty dataset handling
- Pipeline execution
- Cleaned CSV export
- Validation issue summary
- Anomaly results
- Fuzzy duplicate results
- Data drift results
- Error reporting

### Module 10: Interactive Streamlit Dashboard

Location: `dashboard/app.py`

The Streamlit dashboard provides an interactive interface for exploring data quality results.

Implemented capabilities include:

- Dataset upload
- Dataset overview
- Data quality analysis
- Profiling information
- Cleaning and validation results
- Anomaly detection results
- Duplicate detection results
- Data drift analysis
- Integrated pipeline execution
- Optional reference CSV upload
- Cleaned dataset download

### Module 11: Logging and Error Handling

Location: `src/utils/logger.py`

The project uses Python's logging module to record application events.

Implemented features:

- Reusable project logger
- Console logging
- File logging
- DEBUG, INFO, WARNING, and ERROR levels
- Timestamped log messages
- Exception logging
- Automatic log-directory creation
- Prevention of duplicate logger handlers

Log file:

`logs/pipeline.log`

---

## 6. Running the Project

Run commands from the project root directory.

### Step 1: Activate the virtual environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell execution policy prevents activation, use the virtual environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 2: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 3: Run data profiling

```powershell
python src/profiling/profile.py data/raw/dirty_customer_data.csv
```

### Step 4: Run data cleaning

```powershell
python src/cleaning/clean.py
```

### Step 5: Run the complete pipeline using the CLI

```powershell
python -m src.pipeline.cli data/raw/dirty_customer_data.csv
```

The cleaned dataset is saved by default to:

`data/processed/cleaned_data.csv`

### Step 6: Specify a custom output file

```powershell
python -m src.pipeline.cli data/raw/dirty_customer_data.csv --output data/processed/custom_output.csv
```

### Step 7: Run the pipeline with reference data

```powershell
python -m src.pipeline.cli data/raw/dirty_customer_data.csv --reference data/raw/customer_data.csv
```

### Step 8: Run the Streamlit dashboard

```powershell
python -m streamlit run dashboard/app.py
```

Streamlit displays a local URL in the terminal. Open that URL in your browser to use the dashboard.

### Step 9: Run automated tests

```powershell
python -m pytest -v
```

### Step 10: Run tests with coverage

```powershell
python -m pytest --cov=src --cov-report=term-missing -v
```

---

## 7. Dataset Information and Verified Results

The project uses customer datasets containing these fields:

`Customer_ID`, `Name`, `Age`, `Email`, `Phone`, `Gender`, `City`, `Income`, `Purchase_Amount`, and `Purchase_Date`.

Two datasets are available:

- `data/raw/dirty_customer_data.csv` — intentionally contains data quality issues.
- `data/raw/customer_data.csv` — reference customer dataset.

### Dirty dataset characteristics

Previously verified profiling results:

| Metric | Result |
|---|---:|
| Rows | 16 |
| Columns | 10 |
| Duplicate rows | 1 |
| Missing Age values | 1 |
| Missing Email values | 1 |
| Profiling quality score | 95.05 |

Detected PII columns:

- Customer_ID
- Name
- Email
- Phone

### Integrated pipeline verification

A verified pipeline execution on the dirty dataset produced:

| Metric | Result |
|---|---:|
| Original rows | 16 |
| Cleaned rows | 15 |
| Validation issues | 2 |
| Anomalous records | 1 |
| Fuzzy duplicate pairs | 0 |
| Drift results without reference data | 0 |

Missing or invalid email values are reported rather than automatically inventing replacement email addresses.

The anomaly detection result identifies a potentially unusual record, not necessarily an incorrect one.

---

## 8. Automated Testing

The project uses Pytest for unit and integration testing.

Testing includes:

- Data profiling
- Profiling report generation
- Data cleaning
- Data validation rules
- Missing-value imputation
- Anomaly detection
- Fuzzy duplicate detection
- Numerical data drift
- Categorical data drift
- Invalid input handling
- Original DataFrame preservation
- Cleaned dataset verification
- Complete pipeline integration
- CLI execution and output verification
- CLI error handling

### Latest verified test result

**90 tests passed in 22.41 seconds, with 93% overall code coverage.**

Command:

```powershell
python -m pytest -v
```

Result:

```text
collected 90 items

90 passed in 12.53s
```

The 90 passing tests include the existing module tests and 11 new integration tests:

- 7 pipeline integration tests
- 4 CLI integration tests

---

## 9. Development Progress

The project was developed incrementally through the following milestones.

| Development period | Main work |
|---|---|
| Days 1–10 | Repository setup, datasets, initial profiling and cleaning |
| Days 11–15 | Profiling improvements, cleaning and validation |
| Days 16–20 | Testing, profiling restoration, PII detection and reports |
| Day 21 | Rule-based data validation |
| Day 22 | Isolation Forest anomaly detection |
| Day 23 | Advanced missing-value imputation |
| Day 24 | Fuzzy duplicate and data drift detection |
| Day 25 | Streamlit dashboard |
| Day 26 | Integrated data quality pipeline |
| Day 27 | Command-line interface |
| Day 28 | Logging and error handling |
| Day 29 | Pipeline and CLI integration testing |
| Day 30 | Documentation, demo preparation and final repository review |

---

## 10. Future Improvements

Potential improvements include:

- Configurable profiling and validation rules
- More advanced semantic type inference
- Expanded edge-case testing
- Improved anomaly detection evaluation
- More detailed data quality visualizations
- Docker-based deployment
- Performance optimization for larger datasets
- Improved data drift monitoring
- NLP-assisted semantic classification
- Additional reporting and export formats

These are potential enhancements, not claims about features already implemented.

---

## 11. Git and GitHub

**Repository:**
https://github.com/Manolashya/automated-data-quality-system

The project uses Git for version control and GitHub for source code hosting.

Useful commands:

```powershell
git status
git log --oneline -10
git pull origin main
git push origin main
```

Avoid committing virtual environments, secrets, unnecessary cache files, and unrelated temporary files.

---

## 12. Author

**Mano Lashya**

GitHub: [Manolashya](https://github.com/Manolashya)

---

## 13. Project Summary

The Automated Data Cleaning & Validation System is a modular Python-based project that combines data profiling, cleaning, validation, missing-value imputation, anomaly detection, fuzzy duplicate detection, and data drift monitoring.

It integrates these capabilities through a reusable pipeline, command-line interface, and interactive Streamlit dashboard.

Structured logging, error handling, and automated unit and integration tests improve the reliability and maintainability of the system.

The latest verified milestone includes **111 passing automated tests**, demonstrating successful integration of the project's major components.
---

## 14. Day 33 – Data Quality History Tracking

Implemented persistent tracking of successful data quality pipeline executions.

### Features

- Stores pipeline execution history in `reports/quality_history.csv`.
- Records execution timestamp and dataset information.
- Tracks quality score, completeness, missing values, duplicate rows, validation issues, and anomalies.
- Appends new execution records without overwriting previous history.
- Displays the latest quality score and total executions in the Streamlit dashboard.
- Visualizes historical quality scores using a trend chart.
- Displays a table of previous pipeline executions.

### Testing

- Added unit tests for history tracking.
- Added pipeline integration tests.
- Verified CSV creation and multiple execution records.
- Full test suite: **111 passed**.