# Automated Data Cleaning & Validation System

An automated data quality project built with Python and Pandas to profile datasets, identify data quality issues, clean inconsistent data, validate records, and generate profiling reports.

**Project:** CadetX — Hands-On Ecosystem for Junior Data Professionals
**Repository:** [Manolashya/automated-data-quality-system](https://github.com/Manolashya/automated-data-quality-system)
**Development progress:** Through Day 20
**Primary language:** Python

---

## Project Overview

Real-world datasets often contain missing values, duplicate records, inconsistent formats, invalid entries, and unreliable data types. These problems can affect data analysis and downstream applications.

This project aims to automate important data quality tasks through a structured pipeline that includes:

- Dataset profiling and metadata analysis
- Missing-value and duplicate detection
- Data cleaning and transformation
- Rule-based data quality validation
- Quality scoring and JSON report generation
- Automated testing using Pytest

The project is being developed incrementally, with each stage tested and documented before further enhancements are introduced.

---

## Project Objectives

1. Understand the structure and quality of raw datasets.
2. Identify missing values, duplicate records, and invalid entries.
3. Detect semantic column types and potential PII columns.
4. Clean inconsistent data while preserving the original raw dataset.
5. Validate important customer data fields using predefined rules.
6. Generate structured profiling reports.
7. Improve reliability through automated testing and error handling.
8. Maintain a reproducible development history using Git and GitHub.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data loading, profiling, cleaning, and transformation |
| NumPy | Numerical data operations |
| Regular expressions | Email, phone, and identifier pattern checks |
| JSON | Structured profiling report generation |
| Pytest | Automated testing |
| pytest-cov | Test coverage measurement |
| Git | Version control |
| GitHub | Source code hosting and project submission |

Machine learning, NLP, advanced anomaly detection, and production deployment are planned extensions rather than claims about the current implementation.

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
|       |-- clean.py
|
|-- tests/
|   |-- test_profiling.py
|   |-- test_profiling_report.py
|   |-- test_cleaning.py
|   |-- test_cleaning_utils.py
|   |-- test_validation.py
|   |-- test_pipeline.py
|
|-- reports/
|   |-- profiling_report.json
|
|-- README.md
|-- .gitignore
```

The exact contents of folders may evolve during development. Generated reports and processed datasets are excluded from Git tracking where configured by `.gitignore`.

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

The profiler creates a structured JSON report containing information such as:

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

Semantic detection primarily uses column names, and the current mixed-type inspection checks values after Pandas has loaded the CSV. Therefore, it may not detect every inconsistent representation in the original file. More advanced value-level type inference is a potential improvement.

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
- Detect and remove duplicate records where configured.
- Save the cleaned output separately from the raw dataset.

### Data preservation

The raw dataset is retained as the input source. The cleaned dataset is written to:

`data/processed/cleaned_data.csv`

This separation allows the original data to remain available for comparison and reproducibility.

---

## Module 3: Data Quality Validation

The validation functionality checks important customer fields against predefined rules.

Current validation areas include:

- Email format
- Phone number format
- Purchase date validity
- Age range
- Non-negative income
- Non-negative purchase amount
- Allowed gender values
- Allowed city values
- Customer ID format

The profiler calculates field-specific validation percentages and combines available validation scores into an overall quality score.

The overall score depends on the dataset and the validation rules applied. It should be interpreted alongside the individual validation results rather than as a universal measure of dataset correctness.

### Planned enhancements

- Configurable validation rules
- More comprehensive domain-specific constraints
- Advanced imputation strategies
- Machine-learning-based anomaly detection
- NLP-based column classification
- Fuzzy duplicate detection
- Data drift detection

These enhancements require separate implementation and testing before being considered complete.

---

## Module 4: Pipeline Integration and Production Engineering

The project is being developed toward a more reliable end-to-end data quality pipeline.

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
Duplicate Detection
        |
        v
Data Cleaning and Transformation
        |
        v
Missing-Value Handling
        |
        v
Cleaned Dataset
        |
        v
Validation Summary and Reports
```

### Planned production enhancements

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

An intentionally corrupted dataset is used to exercise profiling and validation functionality.

### Verified profiling run

The dirty customer dataset produced the following results during the latest verified run:

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

The profiling script executed successfully, and the generated JSON report was parsed successfully.

These results describe the particular dataset and execution used for verification; other datasets may produce different results.

---

## Running the Project

Run these commands from the project root directory.

### 1. Activate the virtual environment

On Windows CMD:

```cmd
.venv\Scripts\activate
```

### 2. Run data profiling

```cmd
python src\profiling\profile.py data\raw\dirty_customer_data.csv
```

The script prints profiling information and writes the JSON report to `reports/profiling_report.json`.

### 3. Run data cleaning

```cmd
python src\cleaning\clean.py
```

The cleaning script processes the configured raw dataset and writes its output to the configured processed-data path.

### 4. Run automated tests

```cmd
python -m pytest -q
```

### 5. Run tests with coverage

```cmd
python -m pytest --cov=src --cov-report=term-missing -v
```

### 6. Check profiling-script syntax

```cmd
python -m py_compile src\profiling\profile.py
```

---

## Automated Testing and Verification

Pytest is used to test the project modules and important data quality behaviours.

Testing covers areas such as:

- Profiling functionality
- Profiling report contents
- Cleaning behaviour
- Validation rules
- Pipeline execution
- Error-handling scenarios

### Latest verified result

**35 tests passed.**

The profiling script was also executed directly against the dirty customer dataset, and its generated JSON report was verified as valid.

This test count records the latest verified run associated with commit `c72f92f`. It should be updated if the test suite changes.

---

## Development Progress: Days 1–20

The project was developed incrementally, starting with repository setup and data preparation and progressing toward profiling, cleaning, validation, testing, and documentation.

### Early development

- Created the project repository and local development environment.
- Prepared the customer dataset for profiling and cleaning.
- Implemented the initial profiling workflow.
- Developed basic cleaning and transformation functionality.
- Improved numeric conversion and missing-value handling.

### Intermediate development

- Added profiling metadata and statistical analysis.
- Implemented field-specific data validation.
- Added duplicate detection and cleaning checks.
- Developed automated tests for profiling, cleaning, validation, and pipeline behaviour.
- Improved error handling and test coverage.

### Day 16–20: Testing, profiling restoration, and verification

- Continued automated testing of the project modules.
- Improved profiling-script input validation and error handling.
- Restored value-based email and phone detection.
- Restored mixed-type inspection.
- Restored the missing-value matrix and type consistency checks.
- Restored PII and suspicious-column detection.
- Verified profiler execution against the dirty customer dataset.
- Verified JSON report generation.
- Ran the complete test suite successfully with 35 passing tests.
- Committed and pushed the profiling improvements to GitHub.

### Latest milestone commit

`c72f92f` — `Restore profiling analysis features`

The repository's Git history provides the detailed record of the committed changes.

---

## Git and GitHub

The project uses Git for version control and GitHub to host its source code.

Repository:

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
- Improved pipeline orchestration
- Machine-learning-based anomaly detection
- NLP-assisted semantic classification
- Fuzzy duplicate detection
- Data drift monitoring
- Docker-based execution
- Architecture and pipeline documentation
- A final project demonstration

These items represent possible next steps and are not all implemented in the current version.

---

## Author

**Mano Lashya**

GitHub: [Manolashya](https://github.com/Manolashya)

---

## Project Summary

The Automated Data Cleaning & Validation System demonstrates a structured approach to data profiling, cleaning, validation, and report generation using Python and Pandas.

Through incremental implementation and automated testing, the project establishes a foundation for a more comprehensive data quality pipeline. Further enhancements can extend this foundation toward advanced anomaly detection, orchestration, and production-ready data processing.
