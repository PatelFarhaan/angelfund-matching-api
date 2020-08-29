#<==================================================================================================>
#                                        IMPORTS
#<==================================================================================================>
import sys
import time
import threading
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
    total_count = main_db.estimated_document_count()

    for offset in range(0, total_count, doc_limit):
        data_chunk = list(main_db.find({}).skip(offset).limit(doc_limit))

        for doc in data_chunk:
            def helper(email):
                if secondary_collection.find({"email": email}):
                    for k, v in doc.items():
                        if k == "_id":
                            continue
                        try:
                            secondary_collection.update_one({"email": email}, {"$set": {k: v}})
                        except:
                            print("Exception occoured in updating", doc.get("email"))
                else:
                    try:
                        secondary_collection.insert(dict(doc), check_keys=False)
                    except:
                        print("Exception occoured in inserting", doc.get("email"))

            email = doc.get("email")
            thread = threading.Thread(target=helper, args=(email, ))
            thread.start()
        time.sleep(2)


#<==================================================================================================>
#                                   MAIN CALLING FUNCTION
#<==================================================================================================>
insert_into_matching()