"""
Main Entry Point for the Launch Ingester Application.

This script serves as the executable entry point for running the data
ingestion process. It imports the main `run_ingestion` function from the
processors module and calls it.

To run the application, execute this module directly:
    python -m src.launch_ingester.main
"""
import logging
from launch_ingester.processors.ingestion import run_ingestion

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Application starting...")
    run_ingestion()
    logger.info("Application finished.")
