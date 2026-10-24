# Automated Data Cleaning & Validation System

An automated data quality project built with Python and Pandas to profile datasets, identify data quality issues, clean inconsistent data, validate records, detect anomalies, identify potential duplicate records, monitor data drift, and generate profiling reports.

- **Project:** CadetX — Hands-On Ecosystem for Junior Data Professionals
- **Repository:** [Manolashya/automated-data-quality-system](https://github.com/Manolashya/automated-data-quality-system)
- **Development progress:** Through Day 24
- **Primary language:** Python
---

## Project Overview

Real-world datasets often contain missing values, duplicate records, inconsistent formats, invalid entries, and unreliable data types. These problems can affect data analysis and downstream applications.

This project aims to automate important data quality tasks through a collection of modules that includes:

- Dataset profiling and metadata analysis
- Missing-value and duplicate detection
- Data cleaning and transformation
- Rule-based data quality validation
- Advanced missing-value imputation
- Machine-learning-based anomaly detection
- Fuzzy duplicate detection
- Numerical and categorical data drift detection
- Quality scoring and JSON report generation
- Automated testing using Pytest

The project is developed incrementally, with each stage tested and documented before further enhancements are introduced.

---

## Project Objectives

1. Understand the structure and quality of raw datasets.
2. Identify missing values, duplicate records, and invalid entries.
3. Detect semantic column types and potential PII columns.
4. Clean inconsistent data while preserving the original raw dataset.
5. Validate important customer data fields using predefined rules.
6. Generate structured profiling reports.
7. Apply suitable strategies for missing-value imputation.
8. Detect anomalous records using machine learning.
9. Identify potentially duplicated records using fuzzy matching.
10. Detect changes in numerical and categorical data distributions.
11. Improve reliability through automated testing and error handling.
12. Maintain a reproducible development history using Git and GitHub.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data loading, profiling, cleaning, and transformation |
| NumPy | Numerical data operations |
| Scikit-learn | Isolation Forest anomaly detection |
| RapidFuzz | Fuzzy string similarity and duplicate detection |
| Regular expressions | Email, phone, and identifier pattern checks |
| JSON | Structured profiling report generation |
| Pytest | Automated testing |
| pytest-cov | Test coverage measurement |
| Git | Version control |
| GitHub | Source code hosting and project submission |

---

## Project Structure

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
|-- src/
|   |-- profiling/
|   |   |-- profile.py
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
|       |-- detect.py
|
|-- tests/
|   |-- test_anomaly_detection.py
|   |-- test_cleaned_dataset.py
|   |-- test_cleaning.py
|   |-- test_data_drift.py
|   |-- test_duplicate_detection.py
|   |-- test_missing_values.py
|   |-- test_profiling.py
|   |-- test_profiling_report.py
|   |-- test_validation_rules.py
|
|-- reports/
|   |-- profiling_report.json
|
|-- README.md
|-- .gitignore
```

The exact contents of folders may evolve during development. Generated reports, processed datasets, and temporary files are excluded from Git tracking where configured by `.gitignore`.

---

## Module 1: Data Profiling and Metadata Analysis

The profiling module analyses a dataset before cleaning or transformation.

### Implemented features

**1. Dataset overview**

- Row and column counts
- Column names
- Data types
- Missing-value counts
- Duplicate-row counts

**2. Statistical and categorical analysis**

- Numerical statistical summaries
- Cardinality analysis
- Value distributions for supported categorical columns
- Correlation matrix for numerical columns

**3. Semantic column detection**

The profiler classifies columns using their names into categories such as:

- Email
- Phone
- Date
- Name
- ID
- Numeric
- Categorical
- Unknown

**4. Value-based detection**

- Email pattern detection
- Ten-digit phone pattern detection

**5. Data quality analysis**

- Mixed Python data-type inspection
- Missing-value matrix
- Type consistency checks
- PII column detection
- Suspicious-column identification

**6. Profiling report generation**

The profiler creates a structured JSON report containing:

- Dataset shape and column names
- Data types and semantic types
- Missing-value counts and percentages
- Unique-value percentages
- Column completeness scores
- Field-specific validation percentages
- Validation summary and overall quality score
- Duplicate-row count
- Column cardinality
- Detected PII columns

The report is generated at:

`reports/profiling_report.json`

### Current limitations

Semantic detection primarily uses column names, and mixed-type inspection checks values after Pandas has loaded the CSV. Therefore, it may not detect every inconsistent representation in the original file. More advanced value-level type inference is a potential improvement.

---

## Module 2: Data Cleaning and Transformation

The cleaning module transforms the dirty customer dataset into a more consistent form.

### Implemented cleaning operations

- Load the raw CSV dataset.
- Normalize whitespace in applicable values.
- Standardize gender representations, including `M` and `F`.
- Convert invalid numeric entries into missing values where applicable.
- Handle missing values in supported numeric columns.
- Validate email addresses and phone numbers.
- Identify invalid dates.
- Check customer identifiers and categorical fields.
- Detect and remove exact duplicate records where configured.
- Save the cleaned output separately from the raw dataset.

### Data preservation

The raw dataset is retained as the input source. The cleaned dataset is written to:

`data/processed/cleaned_data.csv`

This separation allows the original data to remain available for comparison and reproducibility.

---

## Module 3: Data Quality Validation

The validation module checks important customer fields against predefined rules.

### Implemented validation areas

- Email format
- Phone number format
- Purchase date validity
- Age range
- Non-negative income
- Non-negative purchase amount
- Allowed gender values
- Allowed city values
- Customer ID format
- Required columns and values

The validation functionality identifies invalid and missing values and reports data quality issues.

The profiler also calculates field-specific validation percentages and an overall quality score.

The overall score depends on the dataset and validation rules applied. It should be interpreted alongside individual validation results rather than as a universal measure of dataset correctness.

---

## Module 4: Advanced Missing-Value Imputation

The project includes an advanced missing-value imputation function in:

`src/cleaning/cleaning_utils.py`

### Implemented strategies

- Mean imputation for numerical columns by default.
- Median imputation for numerical columns explicitly selected for median-based replacement.
- Mode imputation for categorical columns.
- Preservation of columns containing only missing values.
- Preservation of the original DataFrame.

The function supports selecting numerical columns that should use median imputation through the `median_columns` parameter.

This allows different imputation strategies to be applied depending on the characteristics of the data.

---

## Module 5: Machine Learning-Based Anomaly Detection

The anomaly detection module uses the Isolation Forest algorithm from Scikit-learn.

Module location:

`src/anomaly_detection/detect.py`

### Implemented features

- Detect unusual observations in numerical data.
- Use Isolation Forest to identify potential anomalies.
- Generate anomaly labels.
- Generate numerical anomaly scores.
- Handle missing values.
- Validate input data and contamination settings.
- Preserve the original DataFrame.

Isolation Forest identifies observations that differ from the general data distribution.

An anomaly detection result indicates a potentially unusual observation. It does not automatically mean that the record is incorrect or should be deleted.

---

## Module 6: Fuzzy Duplicate Detection

The fuzzy duplicate detection module uses RapidFuzz to identify potentially duplicated records based on string similarity.

Module location:

`src/duplicate_detection/detect.py`

### Implemented features

- Compare text values using fuzzy string matching.
- Calculate similarity scores using `fuzz.ratio`.
- Support configurable similarity thresholds.
- Support selecting a column for comparison.
- Perform case-insensitive matching.
- Ignore missing and empty values.
- Return matching row indexes and similarity scores.
- Validate input DataFrames and thresholds.
- Preserve the original DataFrame.

### Example

Two names such as:

- `Rahul Kumar`
- `Rahul Kmar`

can be identified as potentially similar using a configurable similarity threshold.

### Data safety

Fuzzy duplicate detection only reports potential matches. It does not automatically delete or modify records.

This prevents accidental data loss when similar but genuinely different records exist.

---

## Module 7: Data Drift Detection

The data drift module compares a reference dataset with a current dataset to identify changes in data distributions.

Module location:

`src/data_drift/detect.py`

Two statistical approaches are implemented.

### 1. Population Stability Index (PSI)

PSI is used for numerical columns.

It measures how much the distribution of numerical values has changed between the reference and current datasets.

Implemented functionality:

- Create numerical bins using reference dataset quantiles.
- Calculate distributions for both datasets.
- Handle zero-frequency bins using smoothing.
- Calculate the PSI score.
- Identify potential numerical distribution changes using a configurable threshold.

### 2. Total Variation Distance (TVD)

TVD is used for categorical columns.

It measures differences between categorical value distributions.

Implemented functionality:

- Compare category proportions.
- Account for categories present in only one dataset.
- Handle missing values.
- Calculate the TVD score.
- Identify categorical distribution changes using a configurable threshold.

### Additional handling

- Validate input DataFrames.
- Support configurable thresholds and numerical bins.
- Compare only columns present in both datasets.
- Skip columns without usable values.
- Preserve the original datasets.

### Example verification

A manual test compared two datasets with significantly different income distributions but identical city distributions.

The observed results were:

| Column | Method | Drift score | Drift detected |
|---|---|---:|---|
| Income | PSI | 14.506272 | Yes |
| City | TVD | 0.000000 | No |

The result correctly identified the income distribution change while reporting no city distribution drift.

Drift scores should be interpreted according to their respective statistical methods and the selected threshold.

---

## Module 8: Pipeline Integration and Production Engineering

The project is being developed toward a more reliable end-to-end data quality system.

### Current workflow

```text
Raw Customer Dataset
        |
        v
Data Profiling
        |
        v
Data Quality Validation
        |
        v
Data Cleaning and Transformation
        |
        v
Missing-Value Handling
        |
        v
Anomaly Detection
        |
        v
Fuzzy Duplicate Detection
        |
        v
Data Drift Detection
        |
        v
Quality Reports and Analysis
```

The individual modules are implemented and tested. They are not all yet connected through a single automated production pipeline.

### Potential production enhancements

- End-to-end pipeline orchestration
- Command-line interface improvements
- Structured logging
- Expanded error handling
- Docker integration
- Performance improvements
- Additional integration and edge-case tests

These features should be marked complete only after implementation and verification.

---

## Dataset and Profiling Results

The project uses customer data containing fields such as:

`Customer_ID`, `Name`, `Age`, `Email`, `Phone`, `Gender`, `City`, `Income`, `Purchase_Amount`, and `Purchase_Date`.

An intentionally corrupted dataset is used to exercise profiling, cleaning, and validation functionality.

### Previously verified profiling run

The dirty customer dataset produced the following results during a verified profiling run:

| Metric | Result |
|---|---:|
| Rows | 16 |
| Columns | 10 |
| Duplicate rows | 1 |
| Missing Age values | 1 |
| Missing Email values | 1 |
| Overall quality score | 95.05 |

Detected PII columns:

- `Customer_ID`
- `Name`
- `Email`
- `Phone`

These results describe a particular dataset and execution. Other datasets may produce different results.

---

## Running the Project

Run these commands from the project root directory.

### 1. Activate the virtual environment

On Windows CMD:

```cmd
.venv\Scripts\activate
```

### 2. Install required packages

```cmd
python -m pip install pandas numpy scikit-learn rapidfuzz pytest pytest-cov
```

### 3. Run data profiling

```cmd
python src\profiling\profile.py data\raw\dirty_customer_data.csv
```

The script prints profiling information and writes the JSON report to `reports/profiling_report.json`.

### 4. Run data cleaning

```cmd
python src\cleaning\clean.py
```

The cleaning script processes the configured raw dataset and writes its output to the configured processed-data path.

### 5. Run automated tests

```cmd
python -m pytest -v
```

### 6. Run tests with coverage

```cmd
python -m pytest --cov=src --cov-report=term-missing -v
```

### 7. Check Python syntax

For example:

```cmd
python -m py_compile src\data_drift\detect.py
```

---

## Automated Testing and Verification

Pytest is used to test the project modules and important data quality behaviours.

### Testing coverage includes

- Dataset profiling
- Profiling report contents
- Data cleaning
- Data validation rules
- Missing-value imputation
- Anomaly detection
- Fuzzy duplicate detection
- Numerical data drift detection
- Categorical data drift detection
- Invalid inputs and error handling
- Original DataFrame preservation
- Cleaned dataset verification

### Latest verified test result

**79 tests passed in 10.03 seconds.**

The complete test suite was executed using:

```cmd
python -m pytest -v
```

All 79 collected tests passed with zero failures in the latest verified run on October 24, 2026.

---

## Development Progress: Days 1–24

The project was developed incrementally, starting with repository setup and data preparation and progressing toward profiling, cleaning, validation, machine learning, and advanced data quality analysis.

### Days 1–10: Project Setup and Initial Development

- Created the project repository and local development environment.
- Prepared the customer dataset for profiling and cleaning.
- Implemented the initial profiling workflow.
- Developed basic cleaning and transformation functionality.
- Improved numeric conversion and missing-value handling.
- Added project documentation.

### Days 11–15: Profiling and Cleaning Improvements

- Improved data cleaning and validation.
- Enhanced profiling functionality.
- Added more data quality checks.
- Improved handling of invalid and inconsistent values.
- Expanded automated testing.

### Days 16–20: Testing and Profiling Restoration

- Continued automated testing of project modules.
- Improved profiling-script input validation and error handling.
- Restored value-based email and phone detection.
- Restored mixed-type inspection.
- Restored the missing-value matrix and type consistency checks.
- Restored PII and suspicious-column detection.
- Verified profiler execution against the dirty customer dataset.
- Verified JSON report generation.
- Documented project progress through Day 20.

### Day 21: Rule-Based Data Validation

- Implemented rule-based data quality validation.
- Added checks for required values and columns.
- Added age range validation.
- Added email validation.
- Added non-negative income and purchase amount checks.
- Added gender validation.
- Added automated tests for validation rules.

### Day 22: Machine Learning-Based Anomaly Detection

- Implemented anomaly detection using Isolation Forest.
- Added numerical feature handling.
- Generated anomaly labels and scores.
- Added missing-value handling.
- Added input validation and error handling.
- Created automated tests for anomaly detection.

### Day 23: Advanced Missing-Value Imputation

- Implemented mean imputation for numerical columns.
- Implemented configurable median imputation.
- Implemented mode imputation for categorical columns.
- Added handling for entirely missing columns.
- Ensured that original DataFrames remain unchanged.
- Created automated tests for missing-value imputation.

### Day 24: Fuzzy Duplicate Detection and Data Drift Detection

- Installed and integrated RapidFuzz.
- Implemented fuzzy string matching for potential duplicate detection.
- Added configurable similarity thresholds.
- Added case-insensitive matching.
- Ensured missing and empty values are ignored.
- Ensured that fuzzy duplicate detection does not delete records.
- Implemented numerical data drift detection using PSI.
- Implemented categorical data drift detection using TVD.
- Added configurable drift thresholds and numerical bins.
- Added handling for missing values and columns absent from either dataset.
- Created automated tests for fuzzy duplicate detection.
- Created automated tests for numerical and categorical data drift.
- Executed the complete project test suite successfully with 79 passing tests.

---

## Git and GitHub

The project uses Git for version control and GitHub to host its source code.

**Repository:**

https://github.com/Manolashya/automated-data-quality-system

Useful commands:

```cmd
git status
git log --oneline -10
git pull origin main
git push origin main
```

Use focused commits with descriptive messages. Avoid committing virtual environments, generated files, secrets, or unrelated temporary files.

---

## Future Improvements

Potential future improvements include:

- Stronger detection of inconsistent types in raw CSV values
- Configurable profiling and validation rules
- Better reporting of invalid and suspicious records
- More edge-case and regression tests
- End-to-end pipeline orchestration
- Improved command-line interface
- Structured logging
- Docker-based execution
- Performance optimization
- Improved data drift monitoring
- NLP-assisted semantic classification
- Architecture and pipeline documentation
- A final project demonstration

These items represent possible next steps and are not all implemented in the current version.

---

## Author

**Mano Lashya**

GitHub: [Manolashya](https://github.com/Manolashya)

---

## Project Summary

The Automated Data Cleaning & Validation System demonstrates a structured approach to data profiling, cleaning, validation, missing-value imputation, anomaly detection, fuzzy duplicate detection, and data drift monitoring using Python and its data science libraries.

Through incremental implementation, modular development, and automated testing, the project establishes a foundation for a more comprehensive data quality system.

The latest verified development milestone includes 79 passing automated tests and implementations covering both traditional data quality techniques and machine-learning-based analysis.