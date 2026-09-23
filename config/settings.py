from pathlib import Path


# ---------------------------------------------------------
# BASE DIRECTORY
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------
# DATA DIRECTORIES
# ---------------------------------------------------------

DATA_DIR = BASE_DIR / "data"

RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
QUARANTINE_DIR = DATA_DIR / "quarantine"

LOG_DIR = BASE_DIR / "logs"


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

DATABASE_PATH = BASE_DIR / "self_healing.db"


# ---------------------------------------------------------
# FILES
# ---------------------------------------------------------

RAW_DATA_FILE = RAW_DIR / "customers.csv"

PROCESSED_DATA_FILE = PROCESSED_DIR / "customers_clean.csv"

QUARANTINE_FILE = QUARANTINE_DIR / "customers_quarantine.csv"


# ---------------------------------------------------------
# PIPELINE SETTINGS
# ---------------------------------------------------------

MAX_RETRIES = 3

NULL_THRESHOLD = 0.30

DUPLICATE_THRESHOLD = 0.10

DRIFT_THRESHOLD = 0.20


# ---------------------------------------------------------
# EXPECTED SCHEMA
# ---------------------------------------------------------

EXPECTED_COLUMNS = [
    "customer_id",
    "name",
    "age",
    "email",
    "city",
    "purchase_amount",
    "purchase_date",
]


# ---------------------------------------------------------
# CREATE DIRECTORIES
# ---------------------------------------------------------

for directory in [
    RAW_DIR,
    PROCESSED_DIR,
    QUARANTINE_DIR,
    LOG_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)