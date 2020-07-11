#<==================================================================================================>
#                                       IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../")
from pymongo import MongoClient
from project.models import Investor
from common_utilities import CONSTANT
from project.investor.marshmallow_serialize import InvestorDashboardSchema


#<==================================================================================================>
#                                       DB DETAILS
#<==================================================================================================>
def db_details():
    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.users
    return collection


#<==================================================================================================>
#                                 INSERT INTO MATCHING
#<==================================================================================================>
def insert_into_matching(email: str, user_obj: dict) -> bool:
    collection = db_details()
    my_query = {"email": email, "investor": False}

    last_record = collection.find().skip(collection.count() - 1)
    if last_record != []:
        _id = last_record[0]["_id"] + 100
    else:
        _id = 0

    doc = list(collection.find(my_query))
    user_obj["_id"] = _id

    if not doc:
        try:
            collection.insert_one(user_obj)
        except:
            return False
        return True
    else:
        return False


#<==================================================================================================>
#                                UPDATE INTO MATCHING
#<==================================================================================================>
def update_into_matching(email: str, user_obj: dict) -> bool:
    collection = db_details()
    my_query = {"email": email, "investor": False}
    newvalues = {"$set": user_obj}

    try:
        collection.update_one(my_query, newvalues)
    except:
        return False
    return True


#<==================================================================================================>
#                              GET STARTUP MATCHING DATA
#<==================================================================================================>
def get_str_matching_data(email: str) -> object:
    collection = db_details()
    my_query = {"email": email, "investor": False}

    doc = collection.find_one(my_query)
    if not doc:
        return {}
    else:
        return doc


#<==================================================================================================>
#                                   GET STARTUP DETAILS
#<==================================================================================================>
def get_str_details(id: int) -> dict:
    collection = db_details()
    my_query = {"_id": id}
    try:
        em = collection.find_one(my_query)["email"]
    except:
        return {"result": False, "email": None}
    return {"result": True, "email": em}


#<==================================================================================================>
#                                PROCESSING HELPER
#<==================================================================================================>
def processing_helper(email: str) -> dict:
    inv_obj = Investor.objects.filter(email=email).first()
    if not inv_obj:
        return {"result": False, "data": None}

    ma_schema = InvestorDashboardSchema()
    res = ma_schema.dump(inv_obj)
    return {"result": True, "data":res}


#<==================================================================================================>
#                              PROCESS ALL STARTUP DATA
#<==================================================================================================>
def process_all_str_data(data: list) -> list:
    res = []
    for str in data:
        _id = str["_id"]
        str_data = get_str_details(_id)
        if str_data["result"]:
            str_details = processing_helper(str_data["email"])
            if str_details["result"]:
                res.append(str_details["data"])

        if len(res) == 3:
            return res
    return res


#<==================================================================================================>
#                              STARTUP MUTUAL UPDATES
#<==================================================================================================>
def str_mutual_updates(str_obj):
    all_passed = True
    email = str_obj.email
    passed = dict(str_obj.passed)
    pending = dict(str_obj.pending)
    connected = dict(str_obj.connected)

    collection = db_details()
    my_query = {"email": email, "investor": False}
    all_trasactions = [{"passed": passed}, {"pending": pending}, {"connected": connected}]

    for i in all_trasactions:
        newvalues = {"$set": i}

        try:
            collection.update_one(my_query, newvalues)
        except:
            all_passed = False
            continue

    return True if all_passed else False