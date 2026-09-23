import io
import os
import sqlite3
import uuid
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Self-Healing Data Infrastructure",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DARK MODE UI
# ============================================================

st.markdown(
    """
    <style>

    /* MAIN APPLICATION */

    .stApp {
        background-color: #0b1120;
        color: #e5e7eb;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #0b1120;
    }

    [data-testid="stHeader"] {
        background-color: #0b1120;
    }

    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }

    [data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    /* TEXT */

    h1 {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }

    h2 {
        color: #f1f5f9 !important;
    }

    h3 {
        color: #e2e8f0 !important;
    }

    p {
        color: #cbd5e1;
    }

    /* TABS */

    button[data-baseweb="tab"] {
        color: #94a3b8 !important;
        background-color: transparent !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #60a5fa !important;
        font-weight: 700 !important;
    }

    /* METRICS */

    [data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 15px;
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }

    /* BUTTONS */

    .stButton > button {
        background-color: #2563eb;
        color: white;
        border: 1px solid #3b82f6;
        border-radius: 7px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }

    /* DOWNLOAD */

    .stDownloadButton > button {
        background-color: #172554;
        color: #dbeafe;
        border: 1px solid #2563eb;
        border-radius: 7px;
    }

    /* EXPANDERS */

    [data-testid="stExpander"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
    }

    /* FILE UPLOADER */

    [data-testid="stFileUploader"] {
        background-color: #111827;
        border-radius: 8px;
    }

    /* INPUTS */

    input,
    textarea {
        background-color: #111827 !important;
        color: #f8fafc !important;
    }

    /* DIVIDER */

    hr {
        border-color: #1f2937 !important;
    }

    /* CODE */

    code {
        background-color: #111827 !important;
        color: #93c5fd !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

DATABASE_FILE = "self_healing.db"


def initialize_database():
    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            run_time TEXT,
            source TEXT,
            rows_before INTEGER,
            rows_after INTEGER,
            issues_detected INTEGER,
            healing_actions INTEGER,
            status TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS healing_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            event_time TEXT,
            issue_type TEXT,
            action TEXT,
            rows_affected INTEGER
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS lineage_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            event_time TEXT,
            stage TEXT,
            description TEXT
        )
        """
    )

    connection.commit()
    connection.close()


def save_pipeline_run(
    run_id,
    source,
    rows_before,
    rows_after,
    issues_detected,
    healing_actions,
    status,
):
    connection = sqlite3.connect(DATABASE_FILE)

    connection.execute(
        """
        INSERT INTO pipeline_runs
        (
            run_id,
            run_time,
            source,
            rows_before,
            rows_after,
            issues_detected,
            healing_actions,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            source,
            rows_before,
            rows_after,
            issues_detected,
            healing_actions,
            status,
        ),
    )

    connection.commit()
    connection.close()


def save_healing_event(
    run_id,
    issue_type,
    action,
    rows_affected,
):
    connection = sqlite3.connect(DATABASE_FILE)

    connection.execute(
        """
        INSERT INTO healing_events
        (
            run_id,
            event_time,
            issue_type,
            action,
            rows_affected
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            run_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            issue_type,
            action,
            rows_affected,
        ),
    )

    connection.commit()
    connection.close()


def save_lineage(
    run_id,
    stage,
    description,
):
    connection = sqlite3.connect(DATABASE_FILE)

    connection.execute(
        """
        INSERT INTO lineage_events
        (
            run_id,
            event_time,
            stage,
            description
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            run_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            stage,
            description,
        ),
    )

    connection.commit()
    connection.close()


def read_table(table_name):
    connection = sqlite3.connect(DATABASE_FILE)

    dataframe = pd.read_sql_query(
        f"SELECT * FROM {table_name}",
        connection,
    )

    connection.close()

    return dataframe


initialize_database()


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "uploaded_data": None,
    "uploaded_file_name": None,
    "validation": None,
    "cleaned_data": None,
    "final_validation": None,
    "healing_events": [],
    "lineage": [],
    "last_result": None,
    "demo_data": None,
    "demo_cleaned": None,
    "demo_validation": None,
    "demo_final_validation": None,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# DATA LOADING
# ============================================================

def load_file(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):

        return pd.read_csv(uploaded_file)

    if file_name.endswith(".xlsx"):

        return pd.read_excel(
            uploaded_file,
            engine="openpyxl",
        )

    if file_name.endswith(".xls"):

        return pd.read_excel(
            uploaded_file,
        )

    raise ValueError(
        "Unsupported file format."
    )


# ============================================================
# DEMO DATA GENERATOR
# ============================================================

def create_demo_dataset(
    rows=500,
    introduce_errors=True,
):

    np.random.seed(42)

    names = [
        "Rahul",
        "Priya",
        "Arjun",
        "Ananya",
        "Kiran",
        "Sneha",
        "Ravi",
        "Meera",
        "Vikram",
        "Divya",
    ]

    cities = [
        "Hyderabad",
        "Bangalore",
        "Chennai",
        "Mumbai",
        "Delhi",
        "Pune",
    ]

    data = pd.DataFrame(
        {
            "customer_id": range(
                1001,
                1001 + rows,
            ),
            "name": np.random.choice(
                names,
                rows,
            ),
            "age": np.random.randint(
                18,
                70,
                rows,
            ),
            "city": np.random.choice(
                cities,
                rows,
            ),
            "purchase_amount": np.round(
                np.random.uniform(
                    100,
                    50000,
                    rows,
                ),
                2,
            ),
            "email": [
                f"user{i}@example.com"
                for i in range(rows)
            ],
        }
    )

    if introduce_errors and rows >= 20:

        # Missing values
        data.loc[
            5,
            "age",
        ] = np.nan

        data.loc[
            10,
            "city",
        ] = np.nan

        data.loc[
            15,
            "email",
        ] = np.nan

        # Invalid negative value
        data.loc[
            20,
            "purchase_amount",
        ] = -500

        # Invalid age
        data.loc[
            25,
            "age",
        ] = 150

        # Duplicate
        data.loc[
            30
        ] = data.loc[29]

    return data


# ============================================================
# DATA QUALITY ANALYSIS
# ============================================================

def analyze_dataset(dataframe):

    issues = []

    # Empty dataset
    if dataframe.empty:

        issues.append(
            {
                "type": "EMPTY_DATASET",
                "details": "Dataset contains no rows.",
                "rows": 0,
            }
        )

        return issues

    # Missing values
    for column in dataframe.columns:

        missing_count = int(
            dataframe[column]
            .isnull()
            .sum()
        )

        if missing_count > 0:

            issues.append(
                {
                    "type": "MISSING_VALUES",
                    "details": (
                        f"Column '{column}' contains "
                        f"{missing_count} missing value(s)."
                    ),
                    "column": column,
                    "rows": missing_count,
                }
            )

    # Duplicate rows
    duplicate_count = int(
        dataframe.duplicated()
        .sum()
    )

    if duplicate_count > 0:

        issues.append(
            {
                "type": "DUPLICATE_ROWS",
                "details": (
                    f"{duplicate_count} duplicate row(s) detected."
                ),
                "rows": duplicate_count,
            }
        )

    # Negative numeric values
    numeric_columns = dataframe.select_dtypes(
        include=np.number
    ).columns

    for column in numeric_columns:

        negative_count = int(
            (
                dataframe[column]
                < 0
            )
            .sum()
        )

        if negative_count > 0:

            issues.append(
                {
                    "type": "NEGATIVE_VALUES",
                    "details": (
                        f"Column '{column}' contains "
                        f"{negative_count} negative value(s)."
                    ),
                    "column": column,
                    "rows": negative_count,
                }
            )

    # Extreme age values
    for column in dataframe.columns:

        column_name = str(
            column
        ).lower()

        if (
            "age" in column_name
            and pd.api.types.is_numeric_dtype(
                dataframe[column]
            )
        ):

            invalid_age_count = int(
                (
                    (dataframe[column] < 0)
                    | (dataframe[column] > 120)
                )
                .fillna(False)
                .sum()
            )

            if invalid_age_count > 0:

                issues.append(
                    {
                        "type": "INVALID_AGE",
                        "details": (
                            f"Column '{column}' contains "
                            f"{invalid_age_count} invalid age value(s)."
                        ),
                        "column": column,
                        "rows": invalid_age_count,
                    }
                )

    # Infinite values
    for column in numeric_columns:

        infinite_count = int(
            np.isinf(
                dataframe[column]
                .fillna(0)
            )
            .sum()
        )

        if infinite_count > 0:

            issues.append(
                {
                    "type": "INFINITE_VALUES",
                    "details": (
                        f"Column '{column}' contains "
                        f"{infinite_count} infinite value(s)."
                    ),
                    "column": column,
                    "rows": infinite_count,
                }
            )

    return issues


# ============================================================
# SELF HEALING ENGINE
# ============================================================

def heal_dataset(
    dataframe,
    run_id,
):

    cleaned = dataframe.copy()

    healing_events = []

    # --------------------------------------------------------
    # DUPLICATES
    # --------------------------------------------------------

    duplicate_count = int(
        cleaned.duplicated()
        .sum()
    )

    if duplicate_count > 0:

        cleaned = cleaned.drop_duplicates()

        healing_events.append(
            {
                "type": "DUPLICATE_ROWS",
                "action": "Removed duplicate rows",
                "rows": duplicate_count,
            }
        )

        save_healing_event(
            run_id,
            "DUPLICATE_ROWS",
            "Removed duplicate rows",
            duplicate_count,
        )

    # --------------------------------------------------------
    # NUMERIC COLUMNS
    # --------------------------------------------------------

    numeric_columns = cleaned.select_dtypes(
        include=np.number
    ).columns

    for column in numeric_columns:

        # Infinite values
        infinite_mask = np.isinf(
            cleaned[column]
            .fillna(0)
        )

        infinite_count = int(
            infinite_mask.sum()
        )

        if infinite_count > 0:

            cleaned.loc[
                infinite_mask,
                column,
            ] = np.nan

            healing_events.append(
                {
                    "type": "INFINITE_VALUES",
                    "action": (
                        f"Converted infinite values "
                        f"in '{column}' to missing values"
                    ),
                    "rows": infinite_count,
                }
            )

            save_healing_event(
                run_id,
                "INFINITE_VALUES",
                f"Converted infinite values in {column}",
                infinite_count,
            )

        # Age repair
        if "age" in str(column).lower():

            invalid_mask = (
                (cleaned[column] < 0)
                | (cleaned[column] > 120)
            ).fillna(False)

            invalid_count = int(
                invalid_mask.sum()
            )

            if invalid_count > 0:

                valid_values = cleaned.loc[
                    ~invalid_mask,
                    column,
                ].dropna()

                if not valid_values.empty:

                    median_value = valid_values.median()

                    cleaned.loc[
                        invalid_mask,
                        column,
                    ] = median_value

                    healing_events.append(
                        {
                            "type": "INVALID_AGE",
                            "action": (
                                f"Replaced invalid age values "
                                f"with median ({median_value:.2f})"
                            ),
                            "rows": invalid_count,
                        }
                    )

                    save_healing_event(
                        run_id,
                        "INVALID_AGE",
                        (
                            f"Replaced invalid age values "
                            f"with median"
                        ),
                        invalid_count,
                    )

        # Negative values
        negative_mask = (
            cleaned[column] < 0
        ).fillna(False)

        negative_count = int(
            negative_mask.sum()
        )

        if negative_count > 0:

            valid_values = cleaned.loc[
                ~negative_mask,
                column,
            ].dropna()

            if not valid_values.empty:

                median_value = valid_values.median()

                cleaned.loc[
                    negative_mask,
                    column,
                ] = median_value

                healing_events.append(
                    {
                        "type": "NEGATIVE_VALUES",
                        "action": (
                            f"Replaced negative values "
                            f"in '{column}' with median"
                        ),
                        "rows": negative_count,
                    }
                )

                save_healing_event(
                    run_id,
                    "NEGATIVE_VALUES",
                    f"Replaced negative values in {column}",
                    negative_count,
                )

        # Missing numeric values
        missing_mask = cleaned[column].isnull()

        missing_count = int(
            missing_mask.sum()
        )

        if missing_count > 0:

            median_value = cleaned[
                column
            ].median()

            if pd.notna(median_value):

                cleaned.loc[
                    missing_mask,
                    column,
                ] = median_value

                healing_events.append(
                    {
                        "type": "MISSING_VALUES",
                        "action": (
                            f"Filled missing numeric values "
                            f"in '{column}' using median"
                        ),
                        "rows": missing_count,
                    }
                )

                save_healing_event(
                    run_id,
                    "MISSING_VALUES",
                    f"Filled missing numeric values in {column}",
                    missing_count,
                )

    # --------------------------------------------------------
    # TEXT / OBJECT COLUMNS
    # --------------------------------------------------------

    object_columns = cleaned.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in object_columns:

        missing_count = int(
            cleaned[column]
            .isnull()
            .sum()
        )

        if missing_count > 0:

            cleaned[column] = (
                cleaned[column]
                .fillna("Unknown")
            )

            healing_events.append(
                {
                    "type": "MISSING_VALUES",
                    "action": (
                        f"Filled missing text values "
                        f"in '{column}' with 'Unknown'"
                    ),
                    "rows": missing_count,
                }
            )

            save_healing_event(
                run_id,
                "MISSING_VALUES",
                f"Filled missing text values in {column}",
                missing_count,
            )

        # Clean whitespace
        cleaned[column] = (
            cleaned[column]
            .astype(str)
            .str.strip()
        )

    return cleaned, healing_events


# ============================================================
# DRIFT ANALYSIS
# ============================================================

def calculate_drift(
    original,
    cleaned,
):

    results = []

    common_columns = [
        column
        for column in original.columns
        if column in cleaned.columns
    ]

    for column in common_columns:

        original_column = original[
            column
        ]

        cleaned_column = cleaned[
            column
        ]

        if pd.api.types.is_numeric_dtype(
            original_column
        ):

            original_mean = (
                original_column.mean()
            )

            cleaned_mean = (
                cleaned_column.mean()
            )

            if pd.isna(original_mean):
                original_mean = 0

            if pd.isna(cleaned_mean):
                cleaned_mean = 0

            difference = (
                cleaned_mean
                - original_mean
            )

            results.append(
                {
                    "Column": column,
                    "Type": "Numeric",
                    "Original Mean": round(
                        float(original_mean),
                        4,
                    ),
                    "Cleaned Mean": round(
                        float(cleaned_mean),
                        4,
                    ),
                    "Difference": round(
                        float(difference),
                        4,
                    ),
                }
            )

        else:

            original_unique = (
                original_column.nunique()
            )

            cleaned_unique = (
                cleaned_column.nunique()
            )

            results.append(
                {
                    "Column": column,
                    "Type": "Categorical/Text",
                    "Original Unique": int(
                        original_unique
                    ),
                    "Cleaned Unique": int(
                        cleaned_unique
                    ),
                    "Difference": int(
                        cleaned_unique
                        - original_unique
                    ),
                }
            )

    return pd.DataFrame(results)


# ============================================================
# RUN COMPLETE HEALING PIPELINE
# ============================================================

def run_healing_pipeline(
    dataframe,
    source,
):

    run_id = str(
        uuid.uuid4()
    )[:8]

    rows_before = len(
        dataframe
    )

    save_lineage(
        run_id,
        "INGESTION",
        "Dataset successfully loaded.",
    )

    issues = analyze_dataset(
        dataframe
    )

    save_lineage(
        run_id,
        "VALIDATION",
        f"Detected {len(issues)} data-quality issue(s).",
    )

    cleaned, healing_events = heal_dataset(
        dataframe,
        run_id,
    )

    save_lineage(
        run_id,
        "HEALING",
        (
            f"Applied {len(healing_events)} "
            "automatic healing action(s)."
        ),
    )

    final_issues = analyze_dataset(
        cleaned
    )

    save_lineage(
        run_id,
        "REVALIDATION",
        (
            f"Final validation found "
            f"{len(final_issues)} remaining issue(s)."
        ),
    )

    rows_after = len(
        cleaned
    )

    if len(final_issues) == 0:

        status = "HEALED"

    else:

        status = "PARTIALLY HEALED"

    save_lineage(
        run_id,
        "OUTPUT",
        "Cleaned dataset generated.",
    )

    save_pipeline_run(
        run_id,
        source,
        rows_before,
        rows_after,
        len(issues),
        len(healing_events),
        status,
    )

    return {
        "run_id": run_id,
        "issues": issues,
        "cleaned": cleaned,
        "healing_events": healing_events,
        "final_issues": final_issues,
        "status": status,
    }


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "Data Source"
)

data_source = st.sidebar.radio(
    "Choose dataset",
    [
        "Demo Dataset",
        "Upload My Dataset",
    ],
)


# ============================================================
# SIDEBAR — DEMO DATASET
# ============================================================

if data_source == "Demo Dataset":

    st.sidebar.subheader(
        "Demo Settings"
    )

    rows = st.sidebar.number_input(
        "Number of records",
        min_value=100,
        max_value=5000,
        value=500,
        step=100,
    )

    introduce_errors = st.sidebar.checkbox(
        "Introduce simulated failures",
        value=True,
    )

    run_button = st.sidebar.button(
        "🚀 Run Self-Healing Pipeline",
        use_container_width=True,
    )

    if run_button:

        with st.spinner(
            "Running self-healing pipeline..."
        ):

            demo_data = create_demo_dataset(
                rows=int(rows),
                introduce_errors=introduce_errors,
            )

            result = run_healing_pipeline(
                demo_data,
                "Demo Dataset",
            )

            st.session_state[
                "demo_data"
            ] = demo_data

            st.session_state[
                "demo_cleaned"
            ] = result["cleaned"]

            st.session_state[
                "demo_validation"
            ] = result["issues"]

            st.session_state[
                "demo_final_validation"
            ] = result["final_issues"]

            st.session_state[
                "last_result"
            ] = result

        st.sidebar.success(
            "Pipeline completed."
        )


# ============================================================
# SIDEBAR — USER DATASET
# ============================================================

else:

    st.sidebar.subheader(
        "Upload Dataset"
    )

    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV or Excel",
        type=[
            "csv",
            "xlsx",
            "xls",
        ],
    )

    if uploaded_file is not None:

        if (
            st.session_state[
                "uploaded_file_name"
            ]
            != uploaded_file.name
        ):

            try:

                dataframe = load_file(
                    uploaded_file
                )

                st.session_state[
                    "uploaded_data"
                ] = dataframe

                st.session_state[
                    "uploaded_file_name"
                ] = uploaded_file.name

                st.session_state[
                    "validation"
                ] = None

                st.session_state[
                    "cleaned_data"
                ] = None

                st.session_state[
                    "final_validation"
                ] = None

                st.sidebar.success(
                    "Dataset loaded."
                )

            except Exception as error:

                st.sidebar.error(
                    "Could not read file."
                )

                st.sidebar.exception(
                    error
                )
# --------------------------------------------------------
# MAIN HEADER
# --------------------------------------------------------

st.title("🛡️ Self-Healing Data Infrastructure")

st.caption(
    "Autonomous data-quality monitoring, failure detection, "
    "automatic healing, drift detection, and data lineage"
)

st.divider()

# ============================================================
# MAIN TABS
# ============================================================

tabs = st.tabs(
    [
        "🏠 Overview",
        "🔍 Data Quality",
        "🛠️ Self-Healing",
        "📈 Drift Detection",
        "🔗 Data Lineage",
        "📊 Pipeline Runs",
        "📥 Results",
    ]
)


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================

with tabs[0]:

    st.header(
        "🏠 Overview"
    )

    st.markdown(
        """
        ## Self-Healing Data Infrastructure

        An automated data infrastructure system that detects
        data-quality problems, performs automatic recovery,
        revalidates the repaired data and records the complete
        pipeline lifecycle.

        ### Pipeline

        **Ingestion → Validation → Failure Detection → Healing → Revalidation → Output**
        """
    )

    st.divider()

    runs = read_table(
        "pipeline_runs"
    )

    healing = read_table(
        "healing_events"
    )

    lineage = read_table(
        "lineage_events"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Pipeline Runs",
        len(runs),
    )

    c2.metric(
        "Healing Events",
        len(healing),
    )

    c3.metric(
        "Lineage Events",
        len(lineage),
    )

    if data_source == "Demo Dataset":

        current_data = st.session_state[
            "demo_data"
        ]

    else:

        current_data = st.session_state[
            "uploaded_data"
        ]

    if current_data is not None:

        c4.metric(
            "Dataset Rows",
            len(current_data),
        )

        st.success(
            "Dataset is loaded."
        )

    else:

        c4.metric(
            "Dataset Rows",
            0,
        )

        st.info(
            "Use the sidebar to load a dataset."
        )

    st.divider()

    st.subheader(
        "System Architecture"
    )

    architecture_columns = st.columns(6)

    architecture_columns[0].info(
        "📥\n\nIngestion"
    )

    architecture_columns[1].info(
        "🔍\n\nValidation"
    )

    architecture_columns[2].warning(
        "🚨\n\nDetection"
    )

    architecture_columns[3].success(
        "🛠️\n\nHealing"
    )

    architecture_columns[4].info(
        "🔄\n\nRevalidation"
    )

    architecture_columns[5].success(
        "📦\n\nOutput"
    )


# ============================================================
# TAB 2 — DATA QUALITY
# ============================================================

with tabs[1]:

    st.header(
        "🔍 Data Quality"
    )

    if data_source == "Demo Dataset":

        dataframe = st.session_state[
            "demo_data"
        ]

        issues = st.session_state[
            "demo_validation"
        ]

    else:

        dataframe = st.session_state[
            "uploaded_data"
        ]

        issues = st.session_state[
            "validation"
        ]

    if dataframe is None:

        st.info(
            "Load a dataset from the sidebar first."
        )

    else:

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Rows",
            len(dataframe),
        )

        c2.metric(
            "Columns",
            len(dataframe.columns),
        )

        c3.metric(
            "Missing Values",
            int(
                dataframe.isnull()
                .sum()
                .sum()
            ),
        )

        c4.metric(
            "Duplicates",
            int(
                dataframe.duplicated()
                .sum()
            ),
        )

        st.divider()

        if issues is None:

            if st.button(
                "🔎 Analyze Data Quality",
                type="primary",
                use_container_width=True,
            ):

                issues = analyze_dataset(
                    dataframe
                )

                if data_source == "Demo Dataset":

                    st.session_state[
                        "demo_validation"
                    ] = issues

                else:

                    st.session_state[
                        "validation"
                    ] = issues

                st.rerun()

        else:

            if len(issues) == 0:

                st.success(
                    "✅ No major data-quality problems detected."
                )

            else:

                st.warning(
                    f"⚠️ {len(issues)} "
                    "data-quality issue(s) detected."
                )

                for index, issue in enumerate(
                    issues,
                    start=1,
                ):

                    with st.expander(
                        f"Issue {index}: {issue['type']}"
                    ):

                        st.write(
                            issue["details"]
                        )

            st.divider()

            st.subheader(
                "Column Quality"
            )

            quality_rows = []

            for column in dataframe.columns:

                quality_rows.append(
                    {
                        "Column": column,
                        "Type": str(
                            dataframe[column].dtype
                        ),
                        "Missing": int(
                            dataframe[column]
                            .isnull()
                            .sum()
                        ),
                        "Missing %": round(
                            dataframe[column]
                            .isnull()
                            .mean()
                            * 100,
                            2,
                        ),
                        "Unique": int(
                            dataframe[column]
                            .nunique()
                        ),
                    }
                )

            quality_df = pd.DataFrame(
                quality_rows
            )

            st.dataframe(
                quality_df,
                use_container_width=True,
            )


# ============================================================
# TAB 3 — SELF HEALING
# ============================================================

with tabs[2]:

    st.header(
        "🛠️ Self-Healing"
    )

    if data_source == "Demo Dataset":

        dataframe = st.session_state[
            "demo_data"
        ]

        cleaned = st.session_state[
            "demo_cleaned"
        ]

        issues = st.session_state[
            "demo_validation"
        ]

        final_issues = st.session_state[
            "demo_final_validation"
        ]

    else:

        dataframe = st.session_state[
            "uploaded_data"
        ]

        cleaned = st.session_state[
            "cleaned_data"
        ]

        issues = st.session_state[
            "validation"
        ]

        final_issues = st.session_state[
            "final_validation"
        ]

    if dataframe is None:

        st.info(
            "Load a dataset first."
        )

    else:

        st.write(
            "The system automatically repairs common "
            "data-quality problems."
        )

        if issues is None:

            st.warning(
                "Run Data Quality analysis first."
            )

        else:

            st.subheader(
                "Detected Problems"
            )

            if len(issues) == 0:

                st.success(
                    "No problems were detected."
                )

            else:

                for issue in issues:

                    st.write(
                        f"⚠️ **{issue['type']}** — "
                        f"{issue['details']}"
                    )

            st.divider()

            if st.button(
                "🛡️ Start Self-Healing",
                type="primary",
                use_container_width=True,
            ):

                with st.spinner(
                    "Healing dataset..."
                ):

                    result = run_healing_pipeline(
                        dataframe,
                        (
                            "Demo Dataset"
                            if data_source
                            == "Demo Dataset"
                            else "Uploaded Dataset"
                        ),
                    )

                if data_source == "Demo Dataset":

                    st.session_state[
                        "demo_cleaned"
                    ] = result["cleaned"]

                    st.session_state[
                        "demo_validation"
                    ] = result["issues"]

                    st.session_state[
                        "demo_final_validation"
                    ] = result["final_issues"]

                else:

                    st.session_state[
                        "cleaned_data"
                    ] = result["cleaned"]

                    st.session_state[
                        "validation"
                    ] = result["issues"]

                    st.session_state[
                        "final_validation"
                    ] = result["final_issues"]

                st.session_state[
                    "last_result"
                ] = result

                st.success(
                    "Self-healing completed."
                )

                st.rerun()

            if cleaned is not None:

                st.divider()

                st.subheader(
                    "Healing Summary"
                )

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Rows Before",
                    len(dataframe),
                )

                c2.metric(
                    "Rows After",
                    len(cleaned),
                )

                c3.metric(
                    "Healing Actions",
                    len(
                        st.session_state[
                            "last_result"
                        ]["healing_events"]
                    )
                    if st.session_state[
                        "last_result"
                    ]
                    else 0,
                )

                if final_issues is not None:

                    if len(final_issues) == 0:

                        st.success(
                            "✅ Revalidation passed."
                        )

                    else:

                        st.warning(
                            f"⚠️ {len(final_issues)} "
                            "issue(s) remain."
                        )


# ============================================================
# TAB 4 — DRIFT DETECTION
# ============================================================

with tabs[3]:

    st.header(
        "📈 Drift Detection"
    )

    if data_source == "Demo Dataset":

        original = st.session_state[
            "demo_data"
        ]

        cleaned = st.session_state[
            "demo_cleaned"
        ]

    else:

        original = st.session_state[
            "uploaded_data"
        ]

        cleaned = st.session_state[
            "cleaned_data"
        ]

    if original is None:

        st.info(
            "Load a dataset first."
        )

    elif cleaned is None:

        st.info(
            "Run self-healing before checking drift."
        )

    else:

        drift_df = calculate_drift(
            original,
            cleaned,
        )

        if drift_df.empty:

            st.info(
                "No comparable columns found."
            )

        else:

            st.dataframe(
                drift_df,
                use_container_width=True,
                height=500,
            )


# ============================================================
# TAB 5 — DATA LINEAGE
# ============================================================

with tabs[4]:

    st.header(
        "🔗 Data Lineage"
    )

    st.markdown(
        """
        ### Pipeline Lineage

        ```text
        📂 Source Dataset
                ↓
        📥 Ingestion
                ↓
        🔍 Data Validation
                ↓
        🚨 Failure Detection
                ↓
        🛠️ Self-Healing
                ↓
        🔄 Revalidation
                ↓
        📦 Clean Dataset
        ```
        """
    )

    st.divider()

    lineage = read_table(
        "lineage_events"
    )

    if lineage.empty:

        st.info(
            "No lineage events recorded yet."
        )

    else:

        st.dataframe(
            lineage.sort_values(
                "id",
                ascending=False,
            ),
            use_container_width=True,
            height=500,
        )


# ============================================================
# TAB 6 — PIPELINE RUNS
# ============================================================

with tabs[5]:

    st.header(
        "📊 Pipeline Runs"
    )

    runs = read_table(
        "pipeline_runs"
    )

    if runs.empty:

        st.info(
            "No pipeline runs recorded yet."
        )

    else:

        st.dataframe(
            runs.sort_values(
                "id",
                ascending=False,
            ),
            use_container_width=True,
            height=500,
        )

        st.divider()

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total Runs",
            len(runs),
        )

        c2.metric(
            "Healed Runs",
            int(
                (
                    runs["status"]
                    == "HEALED"
                ).sum()
            ),
        )

        c3.metric(
            "Partial Runs",
            int(
                (
                    runs["status"]
                    == "PARTIALLY HEALED"
                ).sum()
            ),
        )


# ============================================================
# TAB 7 — RESULTS
# ============================================================

with tabs[6]:

    st.header(
        "📥 Results"
    )

    if data_source == "Demo Dataset":

        original = st.session_state[
            "demo_data"
        ]

        cleaned = st.session_state[
            "demo_cleaned"
        ]

        final_issues = st.session_state[
            "demo_final_validation"
        ]

    else:

        original = st.session_state[
            "uploaded_data"
        ]

        cleaned = st.session_state[
            "cleaned_data"
        ]

        final_issues = st.session_state[
            "final_validation"
        ]

    if cleaned is None:

        st.info(
            "No cleaned dataset is available yet."
        )

    else:

        st.success(
            "✅ Self-healed dataset is ready."
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Original Rows",
            len(original),
        )

        c2.metric(
            "Final Rows",
            len(cleaned),
        )

        c3.metric(
            "Columns",
            len(cleaned.columns),
        )

        c4.metric(
            "Remaining Issues",
            len(final_issues)
            if final_issues is not None
            else 0,
        )

        st.divider()

        st.subheader(
            "Cleaned Dataset"
        )

        st.dataframe(
            cleaned.head(100),
            use_container_width=True,
            height=450,
        )

        st.divider()

        # CSV DOWNLOAD

        csv_data = cleaned.to_csv(
            index=False
        ).encode(
            "utf-8"
        )

        st.download_button(
            "⬇️ Download Clean CSV",
            data=csv_data,
            file_name="self_healed_dataset.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.write("")

        # EXCEL DOWNLOAD

        try:

            excel_buffer = io.BytesIO()

            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl",
            ) as writer:

                cleaned.to_excel(
                    writer,
                    index=False,
                    sheet_name="Cleaned Data",
                )

            st.download_button(
                "⬇️ Download Clean Excel",
                data=excel_buffer.getvalue(),
                file_name="self_healed_dataset.xlsx",
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                ),
                use_container_width=True,
            )

        except Exception as error:

            st.warning(
                "Excel export could not be created."
            )

            st.caption(
                str(error)
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Self-Healing Data Infrastructure • "
    "Autonomous Data Quality • "
    "Failure Detection • "
    "Automatic Recovery • "
    "Revalidation • "
    "Data Lineage"
)