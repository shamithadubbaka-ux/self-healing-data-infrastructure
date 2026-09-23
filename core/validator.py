import pandas as pd

from config.settings import (
    NULL_THRESHOLD,
    DUPLICATE_THRESHOLD,
)


class ValidationResult:

    def __init__(self):

        self.is_valid = True

        self.issues = []

        self.metrics = {}


def validate_schema(dataframe):

    result = ValidationResult()

    if dataframe.empty:

        result.is_valid = False

        result.issues.append(
            {
                "type": "empty_dataset",
                "details": "Dataset contains zero rows.",
            }
        )

        return result

    result.metrics[
        "row_count"
    ] = len(dataframe)

    result.metrics[
        "column_count"
    ] = len(dataframe.columns)

    return result


def validate_nulls(dataframe):

    result = ValidationResult()

    total_rows = len(dataframe)

    if total_rows == 0:

        return result

    for column in dataframe.columns:

        null_count = dataframe[
            column
        ].isnull().sum()

        null_ratio = (
            null_count / total_rows
        )

        result.metrics[
            f"null_ratio_{column}"
        ] = float(null_ratio)

        if null_ratio > NULL_THRESHOLD:

            result.is_valid = False

            result.issues.append(
                {
                    "type": "high_null_ratio",
                    "column": column,
                    "details": (
                        f"Column '{column}' has "
                        f"{null_ratio:.2%} missing values."
                    ),
                }
            )

    return result


def validate_duplicates(dataframe):

    result = ValidationResult()

    if len(dataframe) == 0:

        return result

    duplicate_count = (
        dataframe.duplicated().sum()
    )

    duplicate_ratio = (
        duplicate_count / len(dataframe)
    )

    result.metrics[
        "duplicate_count"
    ] = int(duplicate_count)

    result.metrics[
        "duplicate_ratio"
    ] = float(duplicate_ratio)

    if duplicate_ratio > DUPLICATE_THRESHOLD:

        result.is_valid = False

        result.issues.append(
            {
                "type": "duplicate_records",
                "details": (
                    f"{duplicate_count} duplicate "
                    "records detected."
                ),
            }
        )

    return result


def detect_numeric_problems(dataframe):

    result = ValidationResult()

    numeric_columns = dataframe.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:

        negative_count = (
            dataframe[column] < 0
        ).sum()

        result.metrics[
            f"negative_values_{column}"
        ] = int(negative_count)

        if negative_count > 0:

            result.is_valid = False

            result.issues.append(
                {
                    "type": "negative_numeric_value",
                    "column": column,
                    "details": (
                        f"{negative_count} negative "
                        f"values found in '{column}'."
                    ),
                }
            )

    return result


def run_validation(dataframe):

    results = []

    results.append(
        validate_schema(dataframe)
    )

    results.append(
        validate_nulls(dataframe)
    )

    results.append(
        validate_duplicates(dataframe)
    )

    results.append(
        detect_numeric_problems(dataframe)
    )

    combined = ValidationResult()

    for result in results:

        if not result.is_valid:

            combined.is_valid = False

        combined.issues.extend(
            result.issues
        )

        combined.metrics.update(
            result.metrics
        )

    return combined