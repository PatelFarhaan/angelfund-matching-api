#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from pymongo import MongoClient
from project.models import Startup
from common_utilities import CONSTANT
from common_utilities.company_images import company_images_api
from project.startup.marshmallow_serialize import StartupDashboardSchema


#<==================================================================================================>
#                                   DATABASE DETAILS
#<==================================================================================================>
def db_details(**kwargs):
    remote_mongo_uri = CONSTANT.CURRENT_DATABASE.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    if kwargs.get("collection"):
        collection_name = kwargs.get("collection")
        collection = db[collection_name]
    else:
        collection = db.users
    return collection


#<==================================================================================================>
#                                INSERTING INTO MATCHING
#<==================================================================================================>
def insert_into_matching(email: str, user_obj: dict) -> bool:
    collection = db_details()
    my_query = {"email": email, "investor": True}

    users_count = collection.estimated_document_count()
    if users_count == 0:
        _id = 0
    else:
        _id = list(collection.find().skip(users_count - 1))[0].get("_id") + 100

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
#                                 UPDATE INTO MATCHING
#<==================================================================================================>
def update_into_matching(email: str, user_obj: dict) -> bool:
    collection = db_details()
    my_query = {"email": email, "investor": True}
    newvalues = {"$set": user_obj}

    try:
        collection.update_one(my_query, newvalues)
    except:
        return False
    return True


#<==================================================================================================>
#                                GET INVESTORS MATCHING DATA
#<==================================================================================================>
def get_inv_matching_data(email: str) -> object:
    collection = db_details()
    my_query = {"email": email, "investor": True}

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
#                                    PROCESSING HELPER
#<==================================================================================================>
def processing_helper(email: str) -> dict:
    str_obj = Startup.objects.filter(email=email).first()
    if not str_obj:
        return {"result": False, "data": None}

    ma_schema = StartupDashboardSchema()
    res = ma_schema.dump(str_obj)
    if res["profile_pic_link"] == None and res["company_link"]:
        try:
            temp = company_images_api(res["company_link"])
            if temp["result"]:
                res["profile_pic_link"] = temp["data"]

            setattr(str_obj, "profile_pic_link", str(temp["data"]))
            str_obj.save()
        except:
            res["profile_pic_link"] = None

    if res["co_founders"]:
        for cf in res["co_founders"]:
            if cf.get("linkedin_link"):
                if not cf.get("linkedin_link").startswith("https://"):
                    linkedin_link = "https://" + cf.get("linkedin_link")
                    cf["linkedin_link"] = linkedin_link

    if res["company_link"]:
        if not res.get("company_link").startswith("https://"):
            company_link = "https://" + res.get("company_link")
            res["company_link"] = company_link

    return {"result": True, "data":res}


#<==================================================================================================>
#                                PROCESS ALL STARTUP DATA
#<==================================================================================================>
def process_all_str_data(data: list) -> list:
    res = []
    duplicate_check = set()

    for str in data:
        _id = str["_id"]
        if _id not in duplicate_check:
            duplicate_check.add(_id)
            str_data = get_str_details(_id)
            if str_data["result"]:
                str_details = processing_helper(str_data["email"])
                if str_details["result"]:
                    res.append(str_details["data"])
        else:
            continue

    return res


#<==================================================================================================>
#                                  INVESTOR MUTUAL UPDATES
#<==================================================================================================>
def inv_mutual_updates(inv_obj):
    all_passed = True
    email = inv_obj.email
    passed = dict(inv_obj.passed)
    pending = dict(inv_obj.pending)
    connected = dict(inv_obj.connected)

    collection = db_details()
    my_query = {"email": email, "investor": True}
    all_trasactions = [{"passed": passed}, {"pending": pending}, {"connected": connected}]

    for i in all_trasactions:
        newvalues = {"$set": i}

        try:
            collection.update_one(my_query, newvalues)
        except:
            all_passed = False
            continue

    return True if all_passed else False