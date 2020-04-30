import sys
sys.path.append("../")
from pymongo import MongoClient
from project.models import Startup
from common_utilities import CONSTANT
from project.startup.marshmallow_serialize import StartupDashboardSchema


def db_details():
    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.users
    return collection


def insert_into_matching():
    collection = db_details()
    my_query = {}

    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.admin
    str_collection = db.startup

    doc = list(collection.find(my_query))
    if doc != []:
        for i in doc:
            i = dict(i)
            i.pop("_id")
            try:
                str_collection.insert_one(i)
            except:
                print("jere")



insert_into_matching()