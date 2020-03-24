import sys
sys.path.append('../')
from pymongo import MongoClient
from common_utilities import CONSTANT


def insert_single_obj_in_database(database, collection, data_obj):
    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client[database]
    collection = db[collection]
    return collection.insert_one(data_obj).acknowledged


def insert_multiple_obj_in_database(database, collection, data_obj):
    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client[database]
    collection = db[collection]
    return collection.insert_many(data_obj).acknowledged