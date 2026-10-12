# Automated Data Cleaning & Validation System

## Project Overview

An automated data quality system designed to profile, clean, validate, and analyze datasets before they are used for further analysis or machine learning.

The project aims to improve data quality by identifying missing values, duplicate records, invalid values, inconsistent formats, and other common data issues through automated profiling and cleaning workflows.

## Project Modules

1. Advanced Data Profiling & Metadata Intelligence
2. Advanced Data Cleaning & Transformation Pipeline
3. AI Validation, Anomaly Detection & Rule Engine
4. Integration, Orchestration & Production Engineering

## Technologies

- Python
- Pandas
- NumPy
- Scikit-learn
- Machine Learning
- Natural Language Processing (NLP)
- Pytest
- Docker
- Git & GitHub

---

## Project Status

### Days 1–10: Project Setup and Data Profiling

#### Project Setup

- Python virtual environment configured
- Project directory structure created
- Git repository initialized
- GitHub repository created and made public
- Project pushed to GitHub

#### Dataset Preparation

- Customer dataset created
- Intentionally corrupted customer dataset created for testing
- Dataset input handling implemented

#### Advanced Data Profiling

- Dataset structure and shape analysis
- Data type detection
- Missing-value analysis
- Duplicate-row detection
- Statistical summaries
- Cardinality analysis
- Value distribution analysis
- Correlation analysis

#### Semantic and Metadata Analysis

- Semantic column detection
- Email, phone, and date pattern detection
- Personally Identifiable Information (PII) column detection
- Mixed-type detection
- Type consistency checking
- Suspicious column detection

#### Data Quality Metrics

- Missing-value percentage
- Unique-value percentage
- Column completeness score
- Email validity percentage
- Phone validity percentage
- Date validity percentage
- Age validity percentage
- Income validity percentage
- Purchase amount validity percentage
- Gender consistency validation
- City consistency validation
- Customer ID format validation

#### Profiling Reports

- Individual validation scores for supported data-quality rules
- Overall validation quality score
- JSON profiling report
- Testing with clean and intentionally corrupted customer datasets

---

## Module 2: Advanced Data Cleaning & Validation Pipeline

### Days 11–15: Cleaning and Validation Improvements

The cleaning pipeline processes the intentionally corrupted customer dataset and saves the cleaned result while preserving the original raw dataset.

#### Data Cleaning Features

- Exact duplicate-row removal
- Whitespace normalization in text columns
- Gender normalization (`M` to `Male` and `F` to `Female`)
- Numeric conversion of Age and Income values
- Invalid Age detection and handling
- Invalid Income detection and handling
- Missing Age imputation using the median
- Missing Income imputation using the median
- Safe median-imputation checks when a median cannot be calculated
- Automatic creation of the output directory when it does not exist
- Cleaned dataset generation

#### Data Validation Features

The pipeline detects invalid or missing values in the following fields:

- Email addresses
- Phone numbers using a basic Indian mobile-number format
- Purchase dates
- Purchase amounts
- Customer IDs
- Gender categories
- City categories
- Age values
- Income values

Validation identifies problems without inventing corrections for invalid email addresses, phone numbers, or purchase dates.

#### Duplicate Customer ID Detection

- Detects repeated `Customer_ID` values before exact duplicate removal
- Reports the number of rows associated with repeated IDs
- Reports the repeated customer ID values
- Removes exact duplicate rows separately

Repeated customer IDs are reported for investigation; the pipeline does not automatically delete different records just because they share an ID.

#### Cleaning Summary

The pipeline reports:

- Original dataset dimensions
- Rows with repeated customer IDs
- Dataset dimensions after exact duplicate removal
- Invalid and missing values detected
- Missing Age and Income values filled
- Validation results for supported fields
- Output file location

#### Reliability Improvements

- Converts Age and Income to numeric values, treating unconvertible values as missing
- Avoids attempting median imputation when no valid median is available
- Creates the output directory automatically before saving the cleaned dataset

### Current Test Dataset Results

The intentionally corrupted customer dataset contains 16 rows and 10 columns before cleaning.

The latest verified cleaning run produced the following results:

| Metric | Result |
|---|---:|
| Original rows | 16 |
| Rows after exact duplicate removal | 15 |
| Output columns | 10 |
| Rows associated with repeated Customer IDs before deduplication | 2 |
| Repeated Customer ID | C015 |
| Missing Age values after cleaning | 0 |
| Missing Income values after cleaning | 0 |
| Invalid Age values after cleaning | 0 |
| Negative Income values after cleaning | 0 |

**Note:** The validation pipeline currently detects certain invalid email, phone, and date values rather than automatically correcting them. The results above describe the current test dataset and are not a guarantee for every possible input dataset.

---

## Current Pipeline

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
Validation Summary
```

## Project Structure

```text
automated-data-quality-system/
|
|-- data/
|   |-- raw/
|   |-- processed/
|
|-- src/
|   |-- profiling/
|   |-- cleaning/
|       |-- clean.py
|
|-- README.md
|-- .gitignore
```

Generated processed CSV files are excluded from Git tracking so that generated datasets do not unnecessarily clutter the repository.

---

## Module 3: Planned AI Validation and Anomaly Detection

The following features are planned for future development and should not be considered fully implemented unless separately completed and tested.

- Advanced rule-based validation engine
- Machine-learning-based anomaly detection
- Advanced imputation strategies
- NLP-based column classification
- Fuzzy duplicate detection
- Data drift detection
- More comprehensive data quality rules
- Automated quality scoring and reporting improvements

## Module 4: Planned Integration and Production Engineering

- End-to-end pipeline orchestration
- Command-line interface (CLI)
- Automated testing with Pytest
- Docker integration
- Improved error handling and logging
- Performance and reliability improvements
- Project documentation and final presentation

---

## Git & GitHub Progress

The project is maintained using Git and GitHub for version control.

Major milestones:

- Initial project setup committed
- Dataset preparation completed
- Advanced profiling and metadata analysis implemented
- Basic cleaning pipeline implemented
- Numeric conversion and missing-value handling improved
- Data validation checks implemented
- Repeated customer ID detection added
- Cleaning output verified using Pandas
- Project progress documented in this README

GitHub repository: https://github.com/Manolashya/automated-data-quality-system

---

## Author

Mano Lashya
