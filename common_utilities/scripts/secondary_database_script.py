#<==================================================================================================>
#                                        IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from pymongo import MongoClient
from common_utilities import CONSTANT


#<==================================================================================================>
#                                        IMPORTS
#<==================================================================================================>
def from_db_details():
    """
    main database details
    """

    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.users
    return collection


#<==================================================================================================>
#                                        IMPORTS
#<==================================================================================================>
def to_db_details():
    """
    secondary database details
    """

    remote_mongo_uri = CONSTANT.SECONDARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.users
    return collection


#<==================================================================================================>
#                                        IMPORTS
#<==================================================================================================>
def insert_into_matching():
    """
    Insert data from main db to secondary db
    """

    doc_limit = 10

    main_db = from_db_details()
    secondary_collection = to_db_details()
    main_count = main_db.estimated_document_count()
    skip_count = secondary_collection.estimated_document_count()

    docs = list(main_db.find().skip(skip_count).limit(doc_limit))
    if docs != []:
        for i in docs:
            try:
                secondary_collection.insert(dict(i), check_keys=False)
            except:
                print("Exception occoured")
    users_count = secondary_collection.estimated_document_count()
    if users_count != main_count:
        return insert_into_matching()


#<==================================================================================================>
#                                   MAIN CALLING FUNCTION
#<==================================================================================================>
insert_into_matching()