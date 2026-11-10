# CadetX — Automated Data Quality System

An end-to-end Python-based data quality platform that automatically cleans, validates, profiles, and monitors datasets. It detects anomalies, identifies potential duplicates, measures data drift, tracks historical quality, compares executions, and generates actionable recommendations through an interactive Streamlit dashboard.

---

## Project Overview

The **Automated Data Quality System** is designed to help data professionals identify and resolve common data quality problems with minimal manual effort.

The system accepts raw datasets, performs multiple data quality operations, and produces structured results that help users understand the condition of their data.

It also maintains execution history and generates prioritized recommendations to guide users toward improving data quality.

### Project Information

- **Project:** CadetX — Automated Data Quality System
- **Development milestone:** Days 1–35 completed
- **Programming language:** Python
- **Primary libraries:** Pandas, NumPy, Scikit-learn, RapidFuzz, Streamlit, Pytest
- **Dashboard:** Streamlit
- **Latest verified test result:** 133 tests passed
- **Repository:** [GitHub Repository](https://github.com/Manolashya/automated-data-quality-system)

---

## Key Features

### 1. Data Profiling
- Analyze dataset structure and dimensions.
- Generate statistical summaries.
- Identify missing values.
- Calculate data completeness.
- Analyze column-level characteristics.
- Generate profiling reports.

### 2. Automated Data Cleaning
- Handle missing values.
- Remove duplicate records.
- Normalize inconsistent values.
- Clean whitespace and formatting issues.
- Export cleaned datasets.

### 3. Data Validation
- Validate required columns.
- Check missing values.
- Validate email formats.
- Validate age ranges.
- Validate gender values.
- Validate numerical constraints.
- Support configurable validation rules through YAML.

### 4. Anomaly Detection
- Detect unusual records using Isolation Forest.
- Identify potential outliers.
- Add anomaly information to analysis results.

### 5. Duplicate Detection
- Identify exact duplicate records.
- Detect potential fuzzy duplicates using RapidFuzz.
- Report similar records for further investigation.

### 6. Data Drift Detection
- Compare datasets against a reference dataset.
- Measure changes in numerical and categorical distributions.
- Use Population Stability Index (PSI) and Total Variation Distance (TVD).
- Generate drift analysis results.

### 7. Integrated Data Quality Pipeline
- Execute multiple data quality operations through one pipeline.
- Combine cleaning, validation, profiling, anomaly detection, duplicate detection, and drift analysis.
- Generate quality reports.
- Save execution history.
- Generate automated recommendations.

### 8. Historical Quality Tracking
- Store quality metrics across pipeline executions.
- Track quality score and completeness.
- Track missing values and duplicate records.
- Maintain a CSV-based execution history.

### 9. Historical Quality Comparison
- Compare the latest execution with the previous execution.
- Identify quality improvements and regressions.
- Compare multiple data quality metrics.
- Display historical changes in the dashboard.

### 10. Automated Data Quality Recommendations
- Generate recommendations based on validation issues.
- Recommend actions for missing and invalid values.
- Identify actions for anomalies and potential duplicates.
- Generate recommendations for detected data drift.
- Identify historical quality regressions.
- Assign High, Medium, and Low priority levels.

### 11. Interactive Streamlit Dashboard
- Upload datasets.
- View dataset information and quality metrics.
- Run the integrated data quality pipeline.
- Explore validation and anomaly results.
- View duplicate and drift analysis.
- Compare historical executions.
- View prioritized recommendations.
- Download cleaned datasets and reports.

### 12. Automated Testing
- Unit tests for individual modules.
- Integration tests for pipeline functionality.
- Tests for historical tracking and comparison.
- Tests for recommendation generation.
- Full project test suite using Pytest.

---

## Project Architecture

```text
automated-data-quality-system/
│
├── config/
│   └── validation_rules.yaml
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── raw/
│   │   └── dirty_customer_data.csv
│   │
│   └── processed/
│       └── customer_data.csv
│
├── reports/
│
├── src/
│   │
│   ├── profiling/
│   │   └── profile.py
│   │
│   ├── cleaning/
│   │
│   ├── validation/
│   │
│   ├── anomaly_detection/
│   │
│   ├── duplicate_detection/
│   │
│   ├── data_drift/
│   │
│   ├── history/
│   │   ├── history_tracker.py
│   │   └── history_comparator.py
│   │
│   ├── recommendations/
│   │   ├── __init__.py
│   │   └── recommendation_engine.py
│   │
│   ├── pipeline/
│   │   ├── runner.py
│   │   └── cli.py
│   │
│   ├── reporting/
│   │   ├── html_report.py
│   │   └── templates/
│   │       └── report_template.html
│   └── utils/
│       ├── logger.py
│       └── config_loader.py
│
├── tests/
│   ├── test_pipeline_integration.py
│   ├── test_history_tracker.py
│   ├── test_history_comparator.py
│   └── test_recommendation_engine.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

*Note: The architecture above highlights the main project modules. Additional implementation and test files are maintained in their respective directories.*

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Dataset manipulation and analysis |
| NumPy | Numerical operations |
| Scikit-learn | Anomaly detection using Isolation Forest |
| RapidFuzz | Fuzzy duplicate detection |
| Streamlit | Interactive dashboard |
| PyYAML | Configurable validation rules |
| Jinja2 | HTML report generation |
| Pytest | Automated testing |
| Git and GitHub | Version control and project hosting |

---

## Installation and Setup

### 1. Clone the repository

```powershell
git clone https://github.com/Manolashya/automated-data-quality-system.git
```

### 2. Navigate to the project directory

```powershell
cd automated-data-quality-system
```

### 3. Create a virtual environment

```powershell
python -m venv .venv
```

### 4. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the virtual environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe
```

### 5. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

---

## Running the Project

### Run the Streamlit Dashboard

From the project root:

```powershell
python -m streamlit run dashboard/app.py
```

The dashboard will open in your browser.

### Run the Data Quality Pipeline

The project provides a pipeline runner and CLI.

To view the available CLI arguments:

```powershell
python -m src.pipeline.cli --help
```

The pipeline can also be called programmatically:

```python
import pandas as pd

from src.pipeline.runner import run_pipeline

df = pd.read_csv("data/raw/dirty_customer_data.csv")

results = run_pipeline(df)

print("Validation issues:", results["validation_issues"])
print("Recommendations:", results["recommendations"])
```

### Run Automated Tests

```powershell
python -m pytest -q
```

---

## Main Project Modules

### Module 1 — Data Profiling

Analyzes the dataset and generates information about its structure, columns, data types, completeness, and statistical characteristics.

### Module 2 — Automated Data Cleaning

Processes raw datasets to address missing values, duplicate records, inconsistent formatting, and other common data quality problems.

### Module 3 — Data Validation

Checks datasets against validation rules and identifies invalid or missing values.

Validation rules can be configured using:

```text
config/validation_rules.yaml
```

### Module 4 — Anomaly Detection

Uses Isolation Forest to identify unusual records that may require additional investigation.

### Module 5 — Duplicate Detection

Uses exact matching and RapidFuzz-based similarity checks to identify duplicate and potentially duplicate records.

### Module 6 — Data Drift Detection

Compares a dataset with a reference dataset to identify changes in numerical and categorical distributions.

### Module 7 — Logging and Error Handling

Provides logging support to help monitor pipeline execution and investigate errors.

### Module 8 — Integrated Data Quality Pipeline

Combines the individual data quality modules into a unified execution workflow.

The pipeline integrates:

1. Data cleaning.
2. Data validation.
3. Dataset profiling.
4. Anomaly detection.
5. Duplicate detection.
6. Data drift detection when a reference dataset is supplied.
7. Quality report generation.
8. Historical execution tracking.
9. Historical quality comparison.
10. Automated recommendation generation.

The pipeline returns structured results that can be used by the dashboard and other project components.

### Module 9 — Command-Line Interface

Provides a command-line entry point for executing the data quality pipeline.

### Module 10 — Interactive Dashboard

The Streamlit dashboard provides an interface for:

- Uploading datasets.
- Viewing dataset information.
- Exploring profiling results.
- Running cleaning and validation.
- Viewing anomaly and duplicate detection results.
- Exploring data drift results.
- Running the integrated pipeline.
- Downloading processed data and reports.
- Viewing historical quality information.
- Comparing recent pipeline executions.
- Viewing automated recommendations.

### Module 11 — Configurable Validation and HTML Reports

Introduces configurable validation rules and HTML report generation.

The validation configuration supports rules such as:

- Required columns.
- Age range.
- Allowed gender values.
- Non-negative income and purchase values.

The reporting module generates HTML reports containing pipeline results.

### Module 12 — Data Quality History Tracking

Introduces persistent tracking of pipeline executions.

The history tracker stores quality information in:

```text
reports/quality_history.csv
```

The recorded information includes:

- Execution timestamp.
- Dataset name.
- Quality score.
- Completeness.
- Missing values.
- Duplicate records.

This allows users to monitor quality across multiple executions instead of viewing only the latest result.

### Module 13 — Data Quality History Comparison

Introduces historical comparison functionality.

The history comparator evaluates recent pipeline executions and identifies changes in data quality.

It supports:

- Latest-versus-previous execution comparison.
- Quality score comparison.
- Completeness comparison.
- Missing value comparison.
- Duplicate record comparison.
- Identification of improvements and regressions.

The dashboard presents these comparisons to help users understand whether data quality is improving or deteriorating.

### Module 14 — Automated Data Quality Recommendations

Introduces an automated recommendation engine in:

```text
src/recommendations/recommendation_engine.py
```

The recommendation engine analyzes pipeline results and generates actionable suggestions.

It considers:

- Validation issues.
- Missing values.
- Invalid email formats.
- Detected anomalies.
- Potential fuzzy duplicates.
- Data drift.
- Historical quality regressions.

Each recommendation contains structured information, including:

- Category.
- Priority.
- Issue description.
- Recommended action.
- Number of affected records.

Recommendations are classified into three priority levels:

| Priority | Meaning |
|---|---|
| High | Important data quality issue requiring attention |
| Medium | Issue that should be reviewed and corrected |
| Low | Lower-priority improvement or monitoring action |

The recommendation engine is integrated into the pipeline, and the dashboard displays recommendation counts, a recommendation table, and detailed actions.

---

## Development Progress

| Development milestone | Work completed |
|---|---|
| Days 1–10 | Project setup, Python foundations, dataset exploration, and initial profiling |
| Days 11–15 | Data cleaning and missing-value handling |
| Days 16–20 | Data validation and validation rules |
| Day 21 | Anomaly detection implementation |
| Day 22 | Duplicate detection implementation |
| Day 23 | Data drift detection |
| Day 24 | Pipeline integration |
| Day 25 | Command-line pipeline execution |
| Day 26 | Logging and error handling |
| Day 27 | Dashboard development |
| Day 28 | Dashboard integration and improvements |
| Day 29 | Automated testing and integration improvements |
| Day 30 | Pipeline completion and project improvements |
| Days 31–32 | Configurable validation and HTML quality reports |
| Day 33 | Persistent data quality history tracking |
| Day 34 | Historical quality comparison and regression detection |
| Day 35 | Automated data quality recommendation engine and dashboard integration |

---

## Automated Testing

The project uses Pytest to verify individual components and integrated workflows.

Test coverage includes:

- Data cleaning.
- Data validation.
- Dataset profiling.
- Anomaly detection.
- Duplicate detection.
- Data drift detection.
- Pipeline execution.
- Pipeline integration.
- Historical quality tracking.
- Historical quality comparison.
- Automated recommendation generation.

### Latest Verified Test Result

```text
133 passed in 11.93s
```

All 133 tests passed in the latest recorded full test-suite execution.

To execute the tests again:

```powershell
python -m pytest -q
```

---

## Day 35 — Automated Data Quality Recommendations

### Objective

Develop an automated recommendation engine that converts detected data quality problems into actionable suggestions.

### Implementation

Created:

```text
src/recommendations/
├── __init__.py
└── recommendation_engine.py
```

The recommendation engine analyzes the output of the integrated pipeline and generates recommendations for detected data quality issues.

### Recommendation Categories

1. Missing required values.
2. Invalid data formats.
3. Unusual records and anomalies.
4. Potential duplicate records.
5. Data distribution drift.
6. Historical quality regressions.

### Priority Classification

Each recommendation is assigned a priority:

- **High:** Important problems that require attention.
- **Medium:** Problems that should be reviewed.
- **Low:** Lower-priority improvements.

### Pipeline Integration

The recommendation engine was integrated into:

```text
src/pipeline/runner.py
```

The pipeline now includes a recommendations result alongside its other data quality outputs.

### Dashboard Integration

The Streamlit dashboard displays:

- Total recommendations.
- High-priority recommendation count.
- Medium-priority recommendation count.
- Low-priority recommendation count.
- A recommendation table.
- Detailed recommended actions.

### Example Execution Result

For the project's dirty customer dataset, the recommendation engine generated:

| Priority | Number of recommendations |
|---|---:|
| High | 2 |
| Medium | 1 |
| Low | 0 |
| **Total** | **3** |

The recommendations included actions for missing email values, unusual records, and invalid email formats.

### Testing

The recommendation engine and pipeline integration were tested as part of the full test suite.

**Latest verified result: 133 tests passed.**

### GitHub

Day 35 implementation commit:

```text
503a4d4 — Add automated data quality recommendations
```

The implementation was pushed to the GitHub `main` branch.

---

## Example Dataset

The project includes a customer dataset containing common data quality problems, such as:

- Missing values.
- Duplicate records.
- Invalid email formats.
- Invalid age values.
- Negative numerical values.
- Invalid phone numbers.
- Invalid dates.
- Inconsistent formatting.

The dataset can be used to demonstrate the cleaning, validation, anomaly detection, duplicate detection, and recommendation features.

---

## Future Improvements

Potential areas for further development include:

- More advanced anomaly detection methods.
- Additional configurable validation rules.
- Improved data drift monitoring.
- More detailed historical analytics and visualizations.
- Support for additional dataset formats.
- Automated data quality notifications.
- Enhanced recommendation explanations.
- Deployment as a web application.

---

## Project Summary

The Automated Data Quality System has evolved from an initial data cleaning and validation project into an integrated data quality platform.

The project currently includes:

- Automated data cleaning.
- Dataset profiling.
- Configurable data validation.
- Anomaly detection.
- Fuzzy duplicate detection.
- Data drift detection.
- Integrated pipeline execution.
- Command-line support.
- Logging and error handling.
- Interactive Streamlit dashboard.
- HTML quality reports.
- Historical quality tracking.
- Historical execution comparison.
- Automated data quality recommendations.
- Priority-based recommendation display.
- Automated testing.

**Development milestone:** Day 35 completed.

**Latest verified automated tests:** 133 passed.

---

## GitHub Repository

Source code and project development history:

[https://github.com/Manolashya/automated-data-quality-system](https://github.com/Manolashya/automated-data-quality-system)

---

## Author

Developed as a hands-on data engineering and data quality project under the CadetX learning journey.