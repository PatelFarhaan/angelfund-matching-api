import sys
sys.path.append("../")
from pymongo import MongoClient
from common_utilities import CONSTANT


def monday_notofications():
    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.users

    my_query = {"monday_notification": True}

    docs = list(collection.find(my_query))
    for doc in docs:
        email = doc["email"]
        if email in ("patel.farhaaan@gmail.com", "colby@angelfund.ai"):
            pass