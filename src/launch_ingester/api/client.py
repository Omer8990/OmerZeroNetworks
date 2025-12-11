"""
API Client for the SpaceX Launches API.

This module provides a client to interact with the SpaceX API (specifically,
the v4 /launches/query endpoint) to fetch launch data. It handles API-side
pagination to ensure all requested launch records are retrieved.
"""
import logging
from typing import List, Optional

import requests
from launch_ingester.config import API_URL
from launch_ingester.models.launch import Launch

logger = logging.getLogger(__name__)


def query_launches(since_date: Optional[str] = None) -> List[Launch]:
    """
    Fetches launch data from the SpaceX API using the /query endpoint.

    This function handles pagination to retrieve all results for the given query.

    Args:
        since_date: If provided, fetches launches with a `date_utc` greater 
                    than this value. Expected format is an ISO 8601 string
                    (e.g., "2020-01-01T00:00:00.000Z").

    Returns:
        A list of Launch objects validated by Pydantic.

    Raises:
        requests.exceptions.RequestException: For connection errors or bad
                                              HTTP status codes.
    """
    all_launches: List[Launch] = []
    page = 1
    has_next_page = True

    base_query = {
        "query": {
        },
        "options": {
            "page": page,
            "limit": 50,
            "sort": {
                "flight_number": "asc"
            },
            "populate": ["payloads"] # Ensures payload data is included
        },
    }

    if since_date:
        base_query["query"]["date_utc"] = {"$gt": since_date}
        logger.info(f"Querying for launches since {since_date}")
    else:
        logger.info("Querying for all launches (backfill).")

    while has_next_page:
        base_query["options"]["page"] = page
        logger.info(f"Fetching page {page} of launch data...")
        
        try:
            response = requests.post(API_URL, json=base_query)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed on page {page}: {e}")
            raise

        launches_on_page = data.get("docs", [])
        logger.info(f"Received {len(launches_on_page)} launches on page {page}.")

        for launch_data in launches_on_page:
            try:
                all_launches.append(Launch(**launch_data))
            except Exception as e:
                # I don't raise the error on purpose here - prioritizing robustness over correctness
                launch_id = launch_data.get("id", "N/A")
                logger.error(f"Pydantic validation failed for launch ID {launch_id}: {e}")

        has_next_page = data.get("hasNextPage", False)
        page += 1
    
    logger.info(f"Finished fetching all pages. Total launches retrieved: {len(all_launches)}")
    return all_launches
