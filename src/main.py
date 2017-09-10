import logging
from typing import Dict, NewType

import bson
import pymongo
import requests

import parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# some additional types defined
PyMongoCollection = NewType("PyMongoCollection", pymongo.collection.Collection)
BsonObjID = NewType("BsonObjID", bson.objectid.ObjectId)


def retrieve_record(url: str) -> str:
    """retrieve record from the url"""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def process(url: str, mongo_col) -> BsonObjID:
    """process record

    retrieve html page, parse it and persist record"""
    logger.info("processing url %s", url)
    r = retrieve_record(url)
    parsed_record = parser.parse(r)
    parsed_record["url"] = url
    logger.debug("parsed record: %s", parsed_record)

    post_id = persist(mongo_col, parsed_record)
    logger.info("post from url %s saved with id %s", url, post_id)

    return post_id


def persist(mongo_col: PyMongoCollection, record: Dict[str, str]):
    logger.info("persisting record: %s", record["url"])
    post_id = mongo_col.insert_one(record).inserted_id
    return post_id


if __name__ == "__main__":
    record_url = "https://sfbay.craigslist.org/sby/mcy/6299581569.html"
    mongo_url = "mongodb://localhost:27017/"

    client = pymongo.MongoClient(mongo_url)
    db = client['craigslist']
    collection = db['r1200gs']

    process(record_url, collection)
