import sys
sys.path.append('../')
from pymongo import MongoClient
from common_utilities import CONSTANT


def search_single_obj_in_database(database, collection, query_obj):
    remote_mongo_uri = CONSTANT.SECONDARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client[database]
    collection = db[collection]
    return collection.find_one(query_obj)


def search_multiple_obj_in_database(database, collection, query_obj):
    remote_mongo_uri = CONSTANT.SECONDARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client[database]
    collection = db[collection]
    return list(collection.find(query_obj))