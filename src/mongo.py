import logging
from typing import Dict

logger = logging.getLogger(__name__)


def persist(record: Dict[str, str]):
    logger.info("persisting record: %s", record["url"])
