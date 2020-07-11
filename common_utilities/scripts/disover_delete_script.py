#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
import sys
import logging
sys.path.append("../../")
from pymongo import MongoClient
from common_utilities import CONSTANT


#<==================================================================================================>
#                                         LOGGER
#<==================================================================================================>
logger = logging.getLogger(__name__)


#<==================================================================================================>
#                                 DELETE DISCOVER COLLECTION
#<==================================================================================================>
def delete_discover_collection():
    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.discover
    collection.delete_many({})


delete_discover_collection()