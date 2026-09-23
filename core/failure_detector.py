from datetime import datetime


def detect_failures(validation_result):

    failures = []

    for issue in validation_result.issues:

        failures.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": issue.get(
                    "type",
                    "unknown",
                ),
                "details": issue.get(
                    "details",
                    "",
                ),
            }
        )

    return failures


def classify_failure(issue_type):

    classifications = {

        "schema_missing_columns":
            "SCHEMA_FAILURE",

        "schema_extra_columns":
            "SCHEMA_WARNING",

        "high_null_ratio":
            "DATA_QUALITY_FAILURE",

        "duplicate_records":
            "DATA_QUALITY_FAILURE",

        "invalid_age":
            "BUSINESS_RULE_FAILURE",

        "negative_purchase":
            "BUSINESS_RULE_FAILURE",

        "empty_dataset":
            "PIPELINE_FAILURE",
    }

    return classifications.get(
        issue_type,
        "UNKNOWN_FAILURE",
    )