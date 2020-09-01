#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from pymongo import MongoClient
from common_utilities import CONSTANT
from project.models import Investor, Startup
from project.startup.marshmallow_serialize import StartupMLSchema
from project.investor.marshmallow_serialize import InvestorMLSchema


#<==================================================================================================>
#                                      ML COLLECTION DETAILS
#<==================================================================================================>
def db_connection_details(database, collection):
    remote_mongo_uri = CONSTANT.CURRENT_DATABASE.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client[database]
    collection = db[collection]
    return collection


#<==================================================================================================>
#                                      ML COLLECTION DETAILS
#<==================================================================================================>
def ml_data_checks(collection: (Investor, Startup)):
    is_inv = True if collection == Investor else False
    all_objs = collection.objects.all()
    serialise_obj = InvestorMLSchema() if is_inv else StartupMLSchema()
    ml_collection = db_connection_details("matching", "users")

    for i in all_objs:
        email = i.email
        my_query = {"email": email, "investor": is_inv}
        ml_rec = ml_collection.find_one(my_query)

        if ml_rec:
            resp = serialise_obj.dump(i)
            for k,v in resp.items():
                ml_rec[k] = v
                newvalues = {"$set": {k: v}}
                ml_collection.update_one(my_query, newvalues)


# ml_data_checks(Investor)