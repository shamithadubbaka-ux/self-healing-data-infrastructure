import pandas as pd

from config.settings import (
    PROCESSED_DATA_FILE,
    QUARANTINE_FILE,
)


def clean_data(dataframe):

    dataframe = dataframe.copy()

    # -----------------------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------------------

    dataframe = dataframe.drop_duplicates()

    # -----------------------------------------------------
    # MISSING VALUE REPAIR
    # -----------------------------------------------------

    for column in dataframe.columns:

        if dataframe[column].isnull().sum() == 0:
            continue

        if pd.api.types.is_numeric_dtype(
            dataframe[column]
        ):

            median_value = dataframe[
                column
            ].median()

            if pd.isna(median_value):

                median_value = 0

            dataframe[column] = dataframe[
                column
            ].fillna(median_value)

        else:

            dataframe[column] = dataframe[
                column
            ].fillna("Unknown")

    # -----------------------------------------------------
    # NUMERIC VALUE REPAIR
    # -----------------------------------------------------

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:

        negative_mask = (
            dataframe[column] < 0
        )

        if negative_mask.any():

            valid_values = dataframe.loc[
                ~negative_mask,
                column,
            ]

            if len(valid_values) > 0:

                replacement = (
                    valid_values.median()
                )

            else:

                replacement = 0

            dataframe.loc[
                negative_mask,
                column,
            ] = replacement

    # -----------------------------------------------------
    # STRING CLEANING
    # -----------------------------------------------------

    object_columns = dataframe.select_dtypes(
        include="object"
    ).columns

    for column in object_columns:

        dataframe[column] = (
            dataframe[column]
            .astype(str)
            .str.strip()
        )

    # -----------------------------------------------------
    # DATE DETECTION
    # -----------------------------------------------------

    for column in dataframe.columns:

        column_name = column.lower()

        if (
            "date" in column_name
            or "time" in column_name
        ):

            converted = pd.to_datetime(
                dataframe[column],
                errors="coerce",
            )

            successful_ratio = (
                converted.notna().mean()
            )

            if successful_ratio > 0.80:

                dataframe[column] = (
                    converted
                )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    dataframe.to_csv(
        PROCESSED_DATA_FILE,
        index=False,
    )

    return dataframe


def quarantine_bad_records(
    original_data
):

    dataframe = original_data.copy()

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) == 0:

        empty = dataframe.iloc[0:0]

        empty.to_csv(
            QUARANTINE_FILE,
            index=False,
        )

        return empty

    bad_mask = pd.Series(
        False,
        index=dataframe.index,
    )

    for column in numeric_columns:

        bad_mask |= (
            dataframe[column] < 0
        )

    bad_records = dataframe[
        bad_mask
    ].copy()

    bad_records.to_csv(
        QUARANTINE_FILE,
        index=False,
    )

    return bad_records