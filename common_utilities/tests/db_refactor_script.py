#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
import sys
import json
sys.path.append("../../")
from pymongo import MongoClient
from common_utilities import CONSTANT
from project.models import Investor, Startup


#<==================================================================================================>
#                                      ML COLLECTION DETAILS
#<==================================================================================================>
def db_connection_details():
    remote_mongo_uri = CONSTANT.CURRENT_DATABASE.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.users
    return collection


#<==================================================================================================>
#                                      ML COLLECTION DETAILS
#<==================================================================================================>
def database_refactor(collection: (Investor, Startup)):
    pass
    is_inv = True if collection == Investor else False
    total_count = collection.objects.count()
    ml_collection = db_connection_details()

    for offset in range(0, total_count + 1, 10):
        data_chunk = list(collection.objects.skip(offset).limit(10))

        for doc in data_chunk:
            email = doc.email
            my_query = {"email": email, "investor": is_inv}
            ml_rec = ml_collection.find_one(my_query)

            if ml_rec:
                co_founders = ml_rec.get("co_founders")
                if co_founders:
                    print(co_founders)
                    for cf_obj in co_founders:
                        temp = None
                        _pic = False
                        for k,v in cf_obj.items():
                            if k == "photo":
                                _pic = True
                                temp = v
                                break

                        if temp or _pic:
                            cf_obj.pop("photo")
                            if not cf_obj.get("profile_image"):
                                cf_obj["profile_image"] = temp
                            else:
                                cf_obj["profile_image"] = None

                            newvalues = {"$set": {"co_founders": [cf_obj]}}
                            ml_collection.update_one(my_query, newvalues)



# database_refactor(Startup)