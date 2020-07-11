# <==================================================================================================>
#                                         IMPORTS
# <==================================================================================================>
import os
import sys
import boto3
import shutil
import requests
sys.path.append("../")
from pymongo import MongoClient
from common_utilities import CONSTANT


#<==================================================================================================>
#                                  SEARCH IN DATABASE
#<==================================================================================================>
def search_in_database(company_name):
    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.images
    collection = db.companies
    return collection.find_one({"company_name": company_name})


#<==================================================================================================>
#                                 INSERTING IN MONGO
#<==================================================================================================>
def insert_in_mongo(company_url, company_name):
    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.images
    collection = db.companies
    collection.insert_one({"company_name": company_name,
                           "logo_url": company_url})


#<==================================================================================================>
#                                 FILE UPLOAD TO S3
#<==================================================================================================>
def file_upload_to_s3(file, object_name):
    object_name = object_name.split('.')[0]
    base_location = f"/{os.getcwd()}/company_images/"
    os.mkdir(base_location)
    file_location = f"{base_location}{object_name}.jpg"

    with open(file_location, 'wb') as f:
        f.write(file.content)

    bucket = 'angelfund-company-images'
    s3_client = boto3.client('s3',
                             aws_access_key_id=CONSTANT.ACCESS_KEY.value,
                             aws_secret_access_key=CONSTANT.ACCESS_VALUE.value
                             )
    object_name = object_name + ".jpg"
    s3_client.upload_file(file_location, bucket, object_name,
                          ExtraArgs={'ACL': 'public-read'})
    public_url = f'https://{bucket}.s3-us-west-1.amazonaws.com/{object_name}'

    shutil.rmtree(base_location)
    return public_url


#<==================================================================================================>
#                                 GET COMPANY IMAGES
#<==================================================================================================>
def get_company_images(company_name):
    client_id = CONSTANT.RITEKIT_KEY.value
    url = "https://api.ritekit.com/v1/images/logo?domain={0}&client_id={1}".format(company_name, client_id)

    response = requests.request("GET", url)
    if response.status_code == 200:
        s3_bucket_uri = file_upload_to_s3(response, company_name)
        insert_in_mongo(s3_bucket_uri, company_name)
        return_obj = {
            "logo_url": s3_bucket_uri,
            "result": True
        }
        return return_obj
    else:
        return {"result": False}


#<==================================================================================================>
#                                COMPANY IMAGES API
#<==================================================================================================>
def company_images_api(company_name):
    company_name = company_name.replace("https://www.", "")
    company_name = company_name.replace("www.", "")
    company_name = company_name.replace("http://www.", "")
    company_name = company_name.replace("http://", "")
    response = search_in_database(company_name)
    if response:
        return_obj = {"result": True, "data": response['logo_url']}
        return return_obj
    else:
        resp = get_company_images(company_name)
        if resp["result"]:
            return_obj = {"result": True, "data": resp["logo_url"]}
            return return_obj
        else:
            return {"result": False, "data": None}