from datetime import datetime

from core.database import save_healing_event
from core.failure_detector import classify_failure
from core.transformer import clean_data


class HealingEngine:

    def __init__(self, run_id):

        self.run_id = run_id

        self.actions = []

    def heal(
        self,
        dataframe,
        failures,
    ):

        repaired_data = dataframe.copy()

        for failure in failures:

            issue_type = failure["type"]

            classification = classify_failure(
                issue_type
            )

            action = self.select_action(
                issue_type
            )

            self.actions.append(
                action
            )

            save_healing_event(
                run_id=self.run_id,
                timestamp=datetime.now().isoformat(),
                issue_type=classification,
                action=action,
                status="STARTED",
                details=failure["details"],
            )

        repaired_data = clean_data(
            repaired_data
        )

        for failure in failures:

            issue_type = failure["type"]

            classification = classify_failure(
                issue_type
            )

            action = self.select_action(
                issue_type
            )

            save_healing_event(
                run_id=self.run_id,
                timestamp=datetime.now().isoformat(),
                issue_type=classification,
                action=action,
                status="SUCCESS",
                details=(
                    "Automatic healing completed."
                ),
            )

        return repaired_data

    @staticmethod
    def select_action(issue_type):

        actions = {

            "schema_missing_columns":
                "STOP_AND_REQUIRE_SCHEMA_REPAIR",

            "schema_extra_columns":
                "IGNORE_EXTRA_COLUMNS",

            "high_null_ratio":
                "IMPUTE_MISSING_VALUES",

            "duplicate_records":
                "REMOVE_DUPLICATES",

            "invalid_age":
                "REPLACE_INVALID_AGE",

            "negative_purchase":
                "REPLACE_INVALID_AMOUNT",

            "empty_dataset":
                "RETRY_PIPELINE",
        }

        return actions.get(
            issue_type,
            "GENERAL_DATA_REPAIR",
        )