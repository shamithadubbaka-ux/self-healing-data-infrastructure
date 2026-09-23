from datetime import datetime

from core.database import save_lineage_event


def record_lineage(
    run_id,
    source,
    transformation,
    destination,
):

    save_lineage_event(
        run_id=run_id,
        timestamp=datetime.now().isoformat(),
        source=source,
        transformation=transformation,
        destination=destination,
    )