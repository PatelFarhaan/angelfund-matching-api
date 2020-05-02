import sys
sys.path.append("../")
from pymongo import MongoClient
from project.models import Startup
from common_utilities import CONSTANT
from common_utilities.company_images import company_images_api
from project.startup.marshmallow_serialize import StartupDashboardSchema  # change to investors


def db_details():
    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.users
    return collection


def insert_into_matching(email: str, user_obj: dict) -> bool:
    collection = db_details()
    my_query = {"email": email, "investor": False}

    _id = (((collection.estimated_document_count()) * 100) + 100)
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


def update_into_matching(email: str, user_obj: dict) -> bool:
    collection = db_details()
    my_query = {"email": email, "investor": False}
    newvalues = {"$set": user_obj}
    try:
        collection.update_one(my_query, newvalues)
    except:
        return False
    return True


def get_matching_data(email: str) -> object:
    collection = db_details()
    my_query = {"email": email, "investor": False}

    doc = collection.find_one(my_query)
    print(doc)
    if not doc:
        return {}
    else:
        return doc


def get_str_details(id: int) -> dict:
    collection = db_details()
    my_query = {"_id": id}
    try:
        em = collection.find_one(my_query)["email"]
    except:
        return {"result": False, "email": None}
    return {"result": True, "email": em}


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
    return {"result": True, "data":res}


def process_all_str_data(data: list) -> list:
    res = []
    for str in data:
        _id = str["_id"]
        str_data = get_str_details(_id)
        if str_data["result"]:
            str_details = processing_helper(str_data["email"])
            if str_details["result"]:
                res.append(str_details["data"])

        if len(res) == 100:
            return res
    return res