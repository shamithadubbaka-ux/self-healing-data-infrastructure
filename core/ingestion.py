import numpy as np
import pandas as pd

from config.settings import RAW_DATA_FILE
from core.logger import get_logger


logger = get_logger()


def generate_sample_data(
    rows=500,
    introduce_errors=True,
):

    np.random.seed(42)

    cities = [
        "Hyderabad",
        "Bangalore",
        "Chennai",
        "Mumbai",
        "Delhi",
        "Pune",
    ]

    names = [
        "Arjun",
        "Priya",
        "Rahul",
        "Ananya",
        "Kiran",
        "Sneha",
        "Ravi",
        "Neha",
    ]

    data = []

    for index in range(rows):

        customer_id = index + 1

        name = np.random.choice(names)

        age = int(np.random.randint(18, 70))

        email = (
            name.lower()
            + str(customer_id)
            + "@example.com"
        )

        city = np.random.choice(cities)

        purchase_amount = round(
            float(np.random.uniform(100, 10000)),
            2,
        )

        purchase_date = pd.Timestamp(
            "2025-01-01"
        ) + pd.Timedelta(
            days=int(
                np.random.randint(0, 365)
            )
        )

        data.append(
            {
                "customer_id": customer_id,
                "name": name,
                "age": age,
                "email": email,
                "city": city,
                "purchase_amount": purchase_amount,
                "purchase_date": purchase_date.strftime(
                    "%Y-%m-%d"
                ),
            }
        )

    dataframe = pd.DataFrame(data)

    if introduce_errors:

        # Missing emails
        missing_email_indices = np.random.choice(
            dataframe.index,
            size=min(8, len(dataframe)),
            replace=False,
        )

        dataframe.loc[
            missing_email_indices,
            "email",
        ] = np.nan

        # Missing cities
        missing_city_indices = np.random.choice(
            dataframe.index,
            size=min(8, len(dataframe)),
            replace=False,
        )

        dataframe.loc[
            missing_city_indices,
            "city",
        ] = np.nan

        # Invalid ages
        invalid_age_indices = np.random.choice(
            dataframe.index,
            size=min(8, len(dataframe)),
            replace=False,
        )

        dataframe.loc[
            invalid_age_indices,
            "age",
        ] = 150

        # Negative purchase amounts
        invalid_amount_indices = np.random.choice(
            dataframe.index,
            size=min(8, len(dataframe)),
            replace=False,
        )

        dataframe.loc[
            invalid_amount_indices,
            "purchase_amount",
        ] = -100

        # Duplicate records
        duplicate_count = min(
            10,
            len(dataframe),
        )

        duplicates = dataframe.sample(
            duplicate_count,
            random_state=10,
        )

        dataframe = pd.concat(
            [
                dataframe,
                duplicates,
            ],
            ignore_index=True,
        )

    dataframe.to_csv(
        RAW_DATA_FILE,
        index=False,
    )

    logger.info(
        "Generated %s raw records.",
        len(dataframe),
    )

    return dataframe


def load_data():

    logger.info(
        "Loading raw data from %s",
        RAW_DATA_FILE,
    )

    return pd.read_csv(
        RAW_DATA_FILE
    )


def load_uploaded_file(uploaded_file):

    """
    Load CSV or Excel files uploaded through Streamlit.
    """

    if uploaded_file is None:
        return None

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):

        dataframe = pd.read_csv(
            uploaded_file
        )

    elif file_name.endswith(
        (".xlsx", ".xls")
    ):

        dataframe = pd.read_excel(
            uploaded_file
        )

    else:

        raise ValueError(
            "Unsupported file format. "
            "Please upload CSV or Excel."
        )

    logger.info(
        "Uploaded dataset loaded: %s",
        uploaded_file.name,
    )

    logger.info(
        "Rows: %s | Columns: %s",
        len(dataframe),
        len(dataframe.columns),
    )

    return dataframe