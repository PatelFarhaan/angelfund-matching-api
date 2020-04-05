import sys
sys.path.append("../")
import csv
from pymongo import MongoClient
from common_utilities import CONSTANT


def investor_data(investor_path):
    collection = db.investor

    input = csv.DictReader(open(investor_path))
    for i in input:
        obj = {}
        for k, v in i.items():
            if k in ("sectors", "syndicate"):
                if v:
                    obj[k] = v.split(',')
                else:
                    obj[k] = []
            else:
                obj[k] = v.strip()
        try:
            collection.insert_one(obj)
        except:
            continue


def startup_data(startup_path):
    collection = db.startup

    input = csv.DictReader(open(startup_path))
    for i in input:
        obj = {}
        for k, v in i.items():
            if k in ("sectors", "startup_progress"):
                if v:
                    obj[k] = v.split(',')
                else:
                    obj[k] = []
            else:
                obj[k] = v.strip()
        try:
            collection.insert_one(obj)
        except:
            continue


if __name__ == '__main__':
    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.admin


    startup_path = "/Users/farhaan/Downloads/Data/startup.csv"     # Make sure to change this to location of startup csv
    investor_path = "/Users/farhaan/Downloads/Data/investor.csv"   # Make sure to change this to location of investor csv

    investor_data(investor_path)
    startup_data(startup_path)