from pymongo import MongoClient

import sys
sys.path.append('../')
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


database = "images"
collection = "companies"
data_obj1 = {
    "company_name" : "farhaans.com",
    "logo_url" : "https://angelfund-company-images.s3-us-west-1.amazonaws.com/tesla.jpg"
}
data_obj2 = {
    "company_name" : "farhaan.com",
    "logo_url" : "https://angelfund-company-images.s3-us-west-1.amazonaws.com/tesla.jpg"
}

resp = insert_multiple_obj_in_database(database, collection, [data_obj1, data_obj2])
print(resp)