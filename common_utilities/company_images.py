import json
import boto3
import requests
from pymongo import MongoClient



def search_in_database(company_name):
    remote_mongo_uri = 'mongodb://***REMOVED***:***REMOVED***@***REMOVED***/admin'
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.images
    collection = db.companies
    return collection.find_one({"company_name": company_name})


def insert_in_mongo(company_url, company_name):
    remote_mongo_uri = 'mongodb://***REMOVED***:***REMOVED***@***REMOVED***/admin'
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.images
    collection = db.companies
    collection.insert_one({"company_name": company_name,
                           "logo_url": company_url
                           })


def file_upload_to_s3(file, object_name):
    object_name = object_name.split('.')[0]
    file_location = f"/tmp/{object_name}.jpg"
    with open(file_location, 'wb') as f:
        f.write(file.content)

    bucket = 'angelfund-company-images'
    s3_client = boto3.client('s3',
                             aws_access_key_id='***REMOVED***',
                             aws_secret_access_key='***REMOVED***'
                             )
    object_name = object_name + ".jpg"
    s3_client.upload_file(file_location, bucket, object_name,
                          ExtraArgs={'ACL': 'public-read'})
    public_url = f'https://{bucket}.s3-us-west-1.amazonaws.com/{object_name}'
    return public_url


def get_company_images(company_name):
    client_id = "810bdfc31d4d73fb97192859a82ee166818cca6e7812"
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


def company_images_api(company_name):
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