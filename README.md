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



\## Module 2 - Basic Data Cleaning



The initial cleaning pipeline currently supports:



\* Duplicate row removal

\* Whitespace normalization

\* Gender value normalization

\* Missing Age imputation using median

\* Cleaned dataset generation



The cleaning pipeline converts the dirty customer dataset into a processed dataset while preserving the original raw dataset.



\---



\## Current Pipeline



```text

Raw Dataset

&#x20;    ↓

Data Profiling

&#x20;    ↓

Data Quality Validation

&#x20;    ↓

Basic Data Cleaning

&#x20;    ↓

Cleaned Dataset

```



\---



\## Current Data Quality Validation



The intentionally corrupted dataset contains issues such as:



\* Missing Age value

\* Missing Email value

\* Invalid email format

\* Invalid phone number

\* Invalid date

\* Age outside the valid range

\* Negative income

\* Inconsistent gender value

\* Inconsistent city value

\* Duplicate customer record



The profiling and validation modules successfully identify these issues and calculate corresponding quality percentages.



\---



\## Git \& GitHub Progress



The project is maintained using Git and GitHub for version control.



Major milestones completed:



\* Initial project setup committed

\* Profiling module implemented

\* Dataset input handling implemented

\* Basic cleaning pipeline implemented

\* Advanced profiling and validation features implemented through Day 10

\* Changes pushed to the `main` branch



\---



\## Next Steps



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



