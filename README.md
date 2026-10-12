\# Automated Data Cleaning \& Validation System



\## Project Overview



An AI-powered data quality system that automatically profiles, cleans, validates, and analyzes datasets before they are used for further analysis or machine learning.



\## Project Modules



1\. Advanced Data Profiling \& Metadata Intelligence

2\. Advanced Data Cleaning \& Transformation Pipeline

3\. AI Validation, Anomaly Detection \& Rule Engine

4\. Integration, Orchestration \& Production Engineering



\## Technologies



\* Python

\* Pandas

\* NumPy

\* Scikit-learn

\* Machine Learning

\* NLP

\* Pytest

\* Docker

\* Git \& GitHub



\## Project Status



\### Days 1–10 Progress



\#### Project Setup



\* Python virtual environment configured

\* Project directory structure created

\* Git repository initialized

\* GitHub repository created and made public

\* Project pushed to GitHub



\#### Dataset Preparation



\* Customer dataset created

\* Intentionally corrupted customer dataset created for testing

\* Dynamic dataset input implemented



\---



\## Module 1 - Advanced Data Profiling \& Metadata Intelligence



The profiling module currently supports:



\### Dataset Profiling



\* Dataset structure analysis

\* Data type detection

\* Missing-value analysis

\* Duplicate detection

\* Statistical summary

\* Cardinality analysis

\* Value distribution analysis

\* Correlation analysis



\### Semantic \& Metadata Analysis



\* Semantic column detection

\* Email, phone, and date pattern detection

\* PII column detection

\* Mixed-type detection

\* Type consistency checking

\* Suspicious column detection



\### Data Quality Metrics



\* Missing-value percentage

\* Unique-value percentage

\* Column completeness score

\* Email validity percentage

\* Phone validity percentage

\* Date validity percentage

\* Age validity percentage

\* Income validity percentage

\* Purchase amount validity percentage

\* Gender consistency validation

\* City consistency validation

\* Customer ID format validation



\### Validation Summary



The profiler generates:



\* Individual validation scores for supported data-quality rules

\* Overall validation quality score

\* JSON profiling report



The profiler has been tested using both clean and intentionally corrupted customer datasets.



\---

## Module 2 - Advanced Data Cleaning & Validation Pipeline

The cleaning pipeline currently supports:

### Data Cleaning

- Duplicate row removal
- Whitespace normalization in text columns
- Gender value normalization (`M` → `Male`, `F` → `Female`)
- Invalid age detection and handling
- Invalid income detection and handling
- Missing Age imputation using the median
- Missing Income imputation using the median
- Processed dataset generation

### Data Validation

The cleaning pipeline detects invalid and missing values in:

- Email addresses
- Phone numbers using a basic Indian mobile-number format
- Purchase dates
- Purchase amounts
- Customer IDs
- Gender categories
- City categories
- Age and Income values

### Cleaning Summary

The pipeline prints a summary of duplicate removal, invalid values detected, missing values handled, and validation results.

Numeric imputation uses median values after invalid Age and Income values are converted to missing values. Invalid email addresses, phone numbers, and purchase dates are detected without inventing corrections or overwriting the original values.

The raw input dataset is preserved, and the cleaned output is generated at `data/processed/cleaned_data.csv`. Generated processed CSV files are excluded from Git tracking.



\### Day 11 Onwards



\* Advanced missing-value handling

\* Data normalization and transformation

\* Fuzzy duplicate detection

\* ML-based imputation

\* Advanced rule-based validation

\* AI-based anomaly detection

\* NLP-based column classification

\* Data drift detection

\* Complete automated pipeline

\* CLI and Docker integration

\* Testing and documentation

\* Final project presentation



\---



\## Author



Mano Lashya



