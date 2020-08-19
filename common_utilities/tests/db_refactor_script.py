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
    # is_inv = True if collection == Investor else False
    # total_count = collection.objects.count()
    # for offset in range(0, total_count + 1, 10):
    #     data_chunk = list(collection.objects.skip(offset).limit(10))
    #
    #     for doc in data_chunk:
    #         try:
    #             print(doc.company_logo_check)
    #             if doc.company_logo_check or doc.company_logo_check == False:
    #                 continue
    #                 # ml_collection = db_connection_details()
    #                 # my_query = {"email": email, "investor": is_inv}
    #                 # ml_rec = ml_collection.find_one(my_query)
    #                 #
    #                 # if ml_rec:
    #                 #     if ml_rec.get("co_founders_check") or ml_rec.get("co_founders_check") == False:
    #                 #         continue
    #                 #     else:
    #                 #         newvalues = {"$set": {"co_founders_check": False}}
    #                 #         ml_collection.update_one(my_query, newvalues)
    #             else:
    #                 continue
    #
    #         except AttributeError as e:
    #             print("here")
    #             doc.company_logo_check = False
    #             doc.save()


# database_refactor(Startup)