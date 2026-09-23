# Self-Healing Data Infrastructure

An autonomous data infrastructure system that detects data quality failures,
schema problems, duplicate records, invalid business values and data drift,
then automatically performs recovery actions.

## Features

- Automated data ingestion
- Data-quality validation
- Schema validation
- Missing-value detection
- Duplicate detection
- Business-rule validation
- Data drift detection
- Failure classification
- Automatic data repair
- Retry and revalidation
- Quarantine support
- Pipeline monitoring
- Data lineage tracking
- SQLite metadata storage
- Streamlit dashboard
- Synthetic failure generation
- No paid APIs
- No cloud dependency

## Architecture

Data Generator
        |
        v
Data Ingestion
        |
        v
Validation
        |
        v
Failure Detection
        |
        v
Healing Engine
        |
        v
Revalidation
        |
        v
Processed Data
        |
        v
Monitoring Dashboard

## Technologies

- Python
- Pandas
- NumPy
- SQLite
- Streamlit
- Plotly

## Running the project

Install dependencies:

```bash
pip install -r requirements.txt