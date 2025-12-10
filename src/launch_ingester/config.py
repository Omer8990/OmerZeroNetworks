"""
Configuration loader for the Launch Ingester application.

This module loads environment variables from a .env file and makes them
available as Python constants. It also validates that all required
variables are present, raising an error if any are missing.
"""

import logging
import os
from dotenv import load_dotenv

# Set up a specific logger for the config module
logger = logging.getLogger(__name__)

# Load environment variables from .env file, overriding any existing OS-level variables.
# This ensures that the project's .env file is the source of truth.
logger.info("Loading environment variables from .env file...")
load_dotenv(override=True)

# --- Environment Variable Definitions ---

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
API_URL = os.getenv("API_URL")

# --- Validation ---

_REQUIRED_VARS = {
    "POSTGRES_USER": POSTGRES_USER,
    "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
    "POSTGRES_DB": POSTGRES_DB,
    "POSTGRES_HOST": POSTGRES_HOST,
    "POSTGRES_PORT": POSTGRES_PORT,
    "API_URL": API_URL,
}

missing_vars = [key for key, value in _REQUIRED_VARS.items() if value is None]

if missing_vars:
    error_message = f"Missing required environment variables: {', '.join(missing_vars)}"
    logger.error(error_message)
    raise ValueError(error_message)

logger.info("All required environment variables are loaded and validated.")
