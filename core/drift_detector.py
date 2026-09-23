import pandas as pd

from config.settings import DRIFT_THRESHOLD


def detect_numeric_drift(
    current_data,
    reference_data,
):

    drift_results = {}

    numeric_columns = current_data.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:

        if column not in reference_data.columns:
            continue

        current_mean = current_data[column].mean()

        reference_mean = reference_data[column].mean()

        if reference_mean == 0:

            drift = 0

        else:

            drift = abs(
                current_mean - reference_mean
            ) / abs(reference_mean)

        drift_results[column] = {
            "drift": float(drift),
            "detected": drift > DRIFT_THRESHOLD,
        }

    return drift_results


def detect_categorical_drift(
    current_data,
    reference_data,
):

    drift_results = {}

    categorical_columns = current_data.select_dtypes(
        include="object"
    ).columns

    for column in categorical_columns:

        if column not in reference_data.columns:
            continue

        current_distribution = (
            current_data[column]
            .value_counts(
                normalize=True
            )
        )

        reference_distribution = (
            reference_data[column]
            .value_counts(
                normalize=True
            )
        )

        categories = set(
            current_distribution.index
        ).union(
            set(reference_distribution.index)
        )

        difference = 0

        for category in categories:

            current_value = current_distribution.get(
                category,
                0,
            )

            reference_value = reference_distribution.get(
                category,
                0,
            )

            difference += abs(
                current_value - reference_value
            )

        drift_results[column] = {
            "drift": float(difference),
            "detected": (
                difference > DRIFT_THRESHOLD
            ),
        }

    return drift_results


def detect_drift(
    current_data,
    reference_data,
):

    numeric = detect_numeric_drift(
        current_data,
        reference_data,
    )

    categorical = detect_categorical_drift(
        current_data,
        reference_data,
    )

    return {
        "numeric": numeric,
        "categorical": categorical,
    }