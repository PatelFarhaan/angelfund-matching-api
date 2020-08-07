#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
from common_utilities.machine_learning.investor_matching_db import db_details


#<==================================================================================================>
#                                        HIDE USER
#<==================================================================================================>
def hide_user(email, id):
    user_obj = {
        "email": email,
        "user_id": id
    }
    collection = db_details(collection="hide_profiles")
    try:
        collection.insert_one(user_obj)
        return True
    except:
        return False


#<==================================================================================================>
#                                        UNHIDE USER
#<==================================================================================================>
def unhide_user(email, id):
    user_obj = {
        "email": email,
        "user_id": id
    }
    collection = db_details(collection="hide_profiles")
    try:
        collection.delete_one(user_obj)
        return True
    except:
        return False