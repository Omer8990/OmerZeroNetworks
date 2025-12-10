import logging
import sys

# Configure a logger for the entire package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)

logger.info("Launch Ingester package initialized.")
