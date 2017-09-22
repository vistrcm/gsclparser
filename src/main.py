import logging
import os
from typing import Dict, NewType

import bson
import pymongo
import requests
from flask import Flask, request, jsonify

import parser

app = Flask(__name__)

debug_set = os.environ.get("DEBUG")
if debug_set is None:
    log_level = logging.INFO
else:
    log_level = logging.DEBUG

logging.basicConfig(level=log_level)
logger = logging.getLogger()

# some additional types defined
PyMongoCollection = NewType("PyMongoCollection", pymongo.collection.Collection)
BsonObjID = NewType("BsonObjID", bson.objectid.ObjectId)

# initialize mongo
# use env variable MONGO_URL to get connection to the mongo server.
# localhost by default
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017/")
logger.info("MONGO_URL: %s", MONGO_URL)
MONGO_CLIENT = pymongo.MongoClient(MONGO_URL)
MONGO_DB = MONGO_CLIENT['craigslist']


def retrieve_record(url: str) -> str:
    """retrieve record from the url"""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def process(url: str, col_name: str) -> str:
    """process record

    retrieve html page, parse it and persist record"""
    logger.info("processing url %s", url)
    r = retrieve_record(url)
    logger.info("record retrieved for url %s", url)
    parsed_record = parser.parse(r)
    parsed_record["url"] = url.decode("utf-8")
    logger.debug("parsed record: %s", parsed_record)

    mongo_col = MONGO_DB[col_name]
    post_id = persist(mongo_col, parsed_record)
    logger.info("post from url %s saved with id %s", url, post_id)
    return str(post_id)


def persist(mongo_col: PyMongoCollection, record: Dict[str, str]):
    logger.info("persisting record: %s", record["url"])
    post_id = mongo_col.insert_one(record).inserted_id
    return post_id


def get_mongo_info() -> Dict[str, int]:
    """show amount of documents per collection"""
    collections = MONGO_DB.collection_names()
    result = {collection: MONGO_DB[collection].count() for collection in collections}
    return result


# flask routes
@app.route("/")
def index():
    return jsonify(get_mongo_info())


@app.route('/<string:collection>', methods=['GET', 'POST'])
def http_handler(collection: str):
    if request.method == 'POST':
        post_url = request.get_data()  # getting raw data
        created_id = process(post_url, collection)
        return created_id
    else:
        return "Hmm. Still... Who are you?"
