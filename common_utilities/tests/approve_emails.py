#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
import sys
import click
sys.path.append("../../")
from pymongo import MongoClient
from common_utilities import CONSTANT


#<==================================================================================================>
#                                   DATABASE CONNECTION DETAILS
#<==================================================================================================>
def db_details(database, collection):
    remote_mongo_uri = CONSTANT.CURRENT_DATABASE.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client[database]
    collection = db[collection]
    return collection


@click.command()
@click.option('--email', '-e', type=str, help="Enter the email address")
def delete_email_address(email: str) -> None:
    ml_collection = db_details("matching", "users")
    inv_collection = db_details("admin", "investor")
    str_collection = db_details("admin", "startup")

    my_query = {"email": email}
    updated_value = { "$set": {"approved": True} }

    ml_query = ml_collection.find_one(my_query)
    inv_query = inv_collection.find_one(my_query)
    str_query = str_collection.find_one(my_query)

    if ml_query:
        ml_collection.update_one(my_query, updated_value)
        print("User Approved from Machine Learning")

    if str_query:
        str_collection.update_one(my_query, updated_value)
        print("User Approved from Startup")

    if inv_query:
        inv_collection.update_one(my_query, updated_value)
        print("User Approved from Investors")


#<==================================================================================================>
#                                   MAIN FUNCTION
#<==================================================================================================>
if __name__ == '__main__':
    delete_email_address()