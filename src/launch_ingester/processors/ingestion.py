
"""
Main Ingestion Processor.

This module orchestrates the entire data ingestion workflow, including:
- Determining whether to run a backfill or an incremental load.
- Fetching the data from the SpaceX API.
- Performing client-side filtering to work around API bugs.
- Inserting the validated and filtered data into the database.
"""
import logging
from datetime import datetime

from launch_ingester.api.client import query_launches
from launch_ingester.database.operations import (
    create_raw_launches_table,
    get_latest_launch_date,
    insert_launch_data,
    create_launch_aggregates_table,
    update_launch_aggregates,
)

logger = logging.getLogger(__name__)


def run_ingestion() -> None:
    """
    Runs the main ingestion process using a backfill/incremental strategy.
    
    1. Ensures the database table exists.
    2. Checks for the most recent launch date in the database to determine
       the run mode (backfill vs. incremental).
    3. Fetches launch data from the API.
    4. Filters out upcoming launches and any launches that are not strictly
       newer than the latest data in the database.
    5. Inserts the new, filtered launch data into the `raw_launches` table.
    """
    logger.info("--- Starting ingestion process ---")

    try:
        # 1. Setup phase
        create_raw_launches_table()
        create_launch_aggregates_table()
        latest_date = get_latest_launch_date()

        # 2. Determine API query parameters
        since_date_iso = None
        if latest_date:
            since_date_iso = latest_date.isoformat()
            logger.info(
                "Database contains prior data. Performing incremental load for launches after "
                f"{since_date_iso}"
            )
        else:
            logger.info("Database is empty. Performing a full backfill of all past launches.")

        # 3. Fetch data from API
        all_launches = query_launches(since_date=since_date_iso)

        # 4. Perform client-side filtering
        # First, filter for past launches to bypass an API bug.
        past_launches = [launch for launch in all_launches if not launch.upcoming]

        # Then, if incremental, filter out records that are not strictly newer.
        if latest_date:
            launches_to_ingest = [
                launch
                for launch in past_launches
                if datetime.fromisoformat(launch.date_utc.replace("Z", "+00:00"))
                > latest_date
            ]
        else:
            launches_to_ingest = past_launches
        
        # 5. Insert data into the database
        if not launches_to_ingest:
            logger.info("No new launches to ingest. Process complete.")
            # Even if there are no new launches, we should update the aggregates
            # in case the underlying data has changed for some reason.
            update_launch_aggregates()
            return

        logger.info(f"Found {len(launches_to_ingest)} new launches to ingest. Inserting into database...")
        for i, launch in enumerate(launches_to_ingest, 1):
            logger.debug(f"Inserting launch {i}/{len(launches_to_ingest)}: {launch.name} ({launch.id})")
            insert_launch_data(launch.dict())

        logger.info(f"Successfully inserted {len(launches_to_ingest)} new launch records.")

        # 6. Update aggregation table
        update_launch_aggregates()

    except Exception as e:
        logger.critical(f"An unhandled error occurred during the ingestion process: {e}", exc_info=True)
    finally:
        logger.info("--- Ingestion process finished ---")
