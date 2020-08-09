#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from pymongo import MongoClient
from common_utilities import CONSTANT
from common_utilities.machine_learning.ml_apis import clear_discover


#<==================================================================================================>
#                                 DELETE DISCOVER COLLECTION
#<==================================================================================================>
def delete_discover_collection():
    clear_discover()


# <==================================================================================================>
#                                   RESET MATCHED PER WEEK
# <==================================================================================================>
def reset_matched_per_week():
    remote_mongo_uri = CONSTANT.CURRENT_DATABASE.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.users
    newvalues = {"$set":{"matched_week": 0}}
    collection.update_many({}, newvalues)


#<==================================================================================================>
#                                    MAIN CALLING FUNCTION
#<==================================================================================================>
delete_discover_collection()
reset_matched_per_week()