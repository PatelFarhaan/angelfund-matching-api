import logging
from pymongo import MongoClient


logger = logging.getLogger(__name__)

# Todo: send a mail to the team when this fails

def delete_discover_collection():
    remote_mongo_uri = "mongodb://***REMOVED***:***REMOVED***@***REMOVED***/admin"
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.discover

    data_chunk = list(collection.find())
    print(data_chunk)


delete_discover_collection()