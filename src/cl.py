import logging

import requests

logger = logging.getLogger(__name__)


def retrieve_record(record_url: str) -> str:
    """retrieve record from the url"""
    response = requests.get(record_url)
    response.raise_for_status()
    return response.text


if __name__ == "__main__":
    url = "https://sfbay.craigslist.org/sby/mcy/6299581569.html"

    record = retrieve_record(url)
    print(record)
