import logging
from typing import Dict

import mongo
import parser
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retrieve_record(url: str) -> str:
    """retrieve record from the url"""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def process(url: str) -> Dict[str, str]:
    logger.info("processing url %s", url)
    r = retrieve_record(url)
    parsed_record = parser.parse(r)
    parsed_record["url"] = url
    logger.debug("parsed record: %s", parsed_record)
    return parsed_record


if __name__ == "__main__":
    mongo_url = "mongodb://localhost:27017/"
    record_url = "https://sfbay.craigslist.org/sby/mcy/6299581569.html"

    processed_record = process(record_url)

    mongo.persist(processed_record)
