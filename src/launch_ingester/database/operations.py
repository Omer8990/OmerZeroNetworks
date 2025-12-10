"""
Database Operations for the Launch Ingester.

This module handles all interactions with the PostgreSQL database, including
establishing connections, creating tables, and inserting data. It uses a
context manager for safe and efficient connection handling.
"""

import json
import logging
import os
from contextlib import contextmanager
from typing import Dict, Optional, Iterator
from datetime import datetime

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection, cursor

from launch_ingester.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)

logger = logging.getLogger(__name__)

# --- Connection Handling ---

@contextmanager
def get_db_connection() -> Iterator[connection]:
    """
    Provides a managed connection to the PostgreSQL database.

    Yields:
        A database connection object.
    
    Raises:
        psycopg2.Error: If a connection to the database cannot be established.
    """
    conn = None
    try:
        logger.debug("Attempting to connect to the PostgreSQL database...")
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
        )
        logger.debug("Database connection established successfully.")
        yield conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed.")

@contextmanager
def get_cursor(conn: connection) -> Iterator[cursor]:
    """
    Provides a cursor for a given database connection, handling commits and rollbacks.
    """
    cur = None
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
        logger.debug("Transaction committed successfully.")
    except psycopg2.Error as e:
        logger.error(f"Database transaction error: {e}")
        if conn:
            conn.rollback()
            logger.warning("Transaction rolled back.")
        raise
    finally:
        if cur:
            cur.close()

# --- Database Functions ---

def create_raw_launches_table() -> None:
    """Creates the `raw_launches` table in the database if it does not exist."""
    # Construct an absolute path to the SQL file relative to this script's location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(current_dir, "../../../sql/create_raw_launches_table.sql")
    
    logger.info("Ensuring 'raw_launches' table exists...")
    try:
        with get_db_connection() as conn, get_cursor(conn) as cur:
            logger.debug(f"Reading table schema from {sql_file_path}")
            with open(sql_file_path, "r") as f:
                cur.execute(f.read())
            logger.info("'raw_launches' table is ready.")
    except (IOError, psycopg2.Error) as e:
        logger.error(f"Failed to create 'raw_launches' table: {e}")
        raise

def get_latest_launch_date() -> Optional[datetime]:
    """
    Retrieves the most recent launch date (UTC) from the `raw_launches` table.

    Returns:
        The most recent launch date as a timezone-aware datetime object,
        or None if the table is empty.
    """
    logger.info("Querying for the most recent launch date in the database.")
    query = "SELECT MAX((launch_data->>'date_utc')::timestamptz) FROM raw_launches;"
    
    try:
        with get_db_connection() as conn, get_cursor(conn) as cur:
            cur.execute(query)
            latest_date = cur.fetchone()[0]
            if latest_date:
                logger.info(f"Most recent launch date found: {latest_date.isoformat()}")
            else:
                logger.info("No existing data found in 'raw_launches' table.")
            return latest_date
    except psycopg2.Error as e:
        logger.error(f"Failed to query for latest launch date: {e}")
        raise

def insert_launch_data(launch_data: Dict) -> None:
    """
    Inserts a new launch record into the `raw_launches` table.
    
    If a launch with the same ID already exists, it is ignored thanks to the
    `ON CONFLICT (id) DO NOTHING` clause in the query.

    Args:
        launch_data: A dictionary representing the launch data to insert.
    """
    insert_query = sql.SQL(
        "INSERT INTO raw_launches (id, launch_data) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING;"
    )
    launch_id = launch_data.get("id")
    
    logger.debug(f"Attempting to insert launch with ID: {launch_id}")
    try:
        with get_db_connection() as conn, get_cursor(conn) as cur:
            cur.execute(insert_query, (launch_id, json.dumps(launch_data)))
            if cur.rowcount > 0:
                logger.debug(f"Successfully inserted launch ID: {launch_id}")
            else:
                logger.debug(f"Launch ID already exists, skipped: {launch_id}")
    except psycopg2.Error as e:
        logger.error(f"Failed to insert launch data for ID {launch_id}: {e}")
        raise
