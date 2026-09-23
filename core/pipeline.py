import uuid
from datetime import datetime

from config.settings import (
    MAX_RETRIES,
    RAW_DATA_FILE,
    PROCESSED_DATA_FILE,
)

from core.database import (
    initialize_database,
    save_pipeline_run,
    save_quality_metric,
)

from core.drift_detector import detect_drift
from core.failure_detector import detect_failures
from core.healing_engine import HealingEngine
from core.ingestion import (
    generate_sample_data,
    load_data,
)
from core.lineage import record_lineage
from core.logger import get_logger
from core.validator import run_validation


logger = get_logger()


class SelfHealingPipeline:

    def __init__(self):

        initialize_database()

    def run(
        self,
        rows=500,
        introduce_errors=True,
    ):

        run_id = str(uuid.uuid4())[:8]

        start_time = datetime.now()

        logger.info(
            "========================================"
        )

        logger.info(
            "Starting Self-Healing Pipeline"
        )

        logger.info(
            "Run ID: %s",
            run_id,
        )

        logger.info(
            "========================================"
        )

        healing_actions = 0

        # -------------------------------------------------
        # DATA GENERATION
        # -------------------------------------------------

        dataframe = generate_sample_data(
            rows=rows,
            introduce_errors=introduce_errors,
        )

        record_lineage(
            run_id,
            "Synthetic Data Generator",
            "Data Generation",
            str(RAW_DATA_FILE),
        )

        # -------------------------------------------------
        # INGESTION
        # -------------------------------------------------

        dataframe = load_data()

        record_lineage(
            run_id,
            str(RAW_DATA_FILE),
            "Data Ingestion",
            "Validation Layer",
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        validation = run_validation(
            dataframe
        )

        logger.info(
            "Initial validation status: %s",
            validation.is_valid,
        )

        # Save metrics
        for metric_name, metric_value in validation.metrics.items():

            metric_status = (
                "PASS"
                if isinstance(
                    metric_value,
                    (int, float),
                )
                else "INFO"
            )

            save_quality_metric(
                run_id,
                metric_name,
                float(metric_value)
                if isinstance(
                    metric_value,
                    (int, float),
                )
                else 0,
                metric_status,
            )

        # -------------------------------------------------
        # FAILURE DETECTION
        # -------------------------------------------------

        failures = detect_failures(
            validation
        )

        # -------------------------------------------------
        # SELF HEALING
        # -------------------------------------------------

        if failures:

            logger.warning(
                "Detected %s issues.",
                len(failures),
            )

            engine = HealingEngine(
                run_id
            )

            dataframe = engine.heal(
                dataframe,
                failures,
            )

            healing_actions = len(
                engine.actions
            )

            record_lineage(
                run_id,
                "Validation Layer",
                "Automatic Healing",
                "Clean Data",
            )

        else:

            logger.info(
                "No failures detected."
            )

        # -------------------------------------------------
        # RETRY / REVALIDATION
        # -------------------------------------------------

        final_validation = None

        for attempt in range(
            1,
            MAX_RETRIES + 1,
        ):

            logger.info(
                "Validation attempt %s/%s",
                attempt,
                MAX_RETRIES,
            )

            final_validation = run_validation(
                dataframe
            )

            if final_validation.is_valid:

                logger.info(
                    "Data successfully healed."
                )

                break

            logger.warning(
                "Validation still failing."
            )

        # -------------------------------------------------
        # DRIFT DETECTION
        # -------------------------------------------------

        reference_data = generate_sample_data(
            rows=rows,
            introduce_errors=False,
        )

        drift_results = detect_drift(
            dataframe,
            reference_data,
        )

        drift_count = 0

        for category in drift_results.values():

            for result in category.values():

                if result["detected"]:

                    drift_count += 1

        save_quality_metric(
            run_id,
            "drift_count",
            drift_count,
            "PASS"
            if drift_count == 0
            else "WARNING",
        )

        # -------------------------------------------------
        # FINAL STATUS
        # -------------------------------------------------

        if (
            final_validation
            and final_validation.is_valid
        ):

            status = "HEALED"

            message = (
                "Pipeline completed successfully "
                "with automatic recovery."
            )

        else:

            status = "FAILED"

            message = (
                "Pipeline could not fully recover."
            )

        end_time = datetime.now()

        save_pipeline_run(
            run_id=run_id,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            status=status,
            rows_processed=len(dataframe),
            rows_failed=len(failures),
            healing_actions=healing_actions,
            message=message,
        )

        record_lineage(
            run_id,
            "Clean Data",
            "Final Persistence",
            str(PROCESSED_DATA_FILE),
        )

        logger.info(
            "Pipeline status: %s",
            status,
        )

        logger.info(
            "Rows processed: %s",
            len(dataframe),
        )

        logger.info(
            "Healing actions: %s",
            healing_actions,
        )

        return {
            "run_id": run_id,
            "status": status,
            "rows_processed": len(dataframe),
            "rows_failed": len(failures),
            "healing_actions": healing_actions,
            "message": message,
        }