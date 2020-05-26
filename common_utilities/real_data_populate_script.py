import sys
sys.path.append("../")
import csv
import ast
import json
import pandas as pd
from pymongo import MongoClient
from common_utilities import CONSTANT
from project.models import Startup, Investor
from project.startup.marshmallow_serialize import StartupMLSchema
from project.investor.marshmallow_serialize import InvestorMLSchema


def investor_data(investor_path):
    ma_schema = InvestorMLSchema()
    sectors_det = sectors_data()
    csv_path = convert_excel_to_csv(investor_path, True)

    collection = db_connection_details()

    input = csv.DictReader(open(csv_path))
    for i in input:
        i = dict(i)
        del i['']
        i["deals"] = [i["deals"]]
        try:
            i["prior_investments"] = [json.loads(json.dumps(i)) for i in ast.literal_eval(i["prior_investments"])]
        except:
            i["prior_investments"] = []
        i["sectors"] = [sectors_det[i.strip()] for i in i["sectors"].split(',')]
        i["syndicate"] = [i.strip() for i in i["syndicate"].split(',') if i.strip() != ""]
        try:
            i["accreditation"] = str(int(float(i["accreditation"])))
        except:
            i["accreditation"] = "nothing"
        i["email_confirmed"] = True
        i["approved"] =  True


        email = i["email"]
        users_count = collection.estimated_document_count()
        if users_count == 0:
            _id = 0
        else:
            _id = (((users_count - 1) * 100) + 100)

        new_obj = Investor(**i)
        new_obj.save()

        inv_obj = Investor.objects.filter(email=email).first()
        resp = ma_schema.dump(inv_obj)
        resp["_id"] = _id
        collection.insert_one(resp)
    print("All investors data inserted successfully!!!")



def startup_data(startup_path):
    collection = db_connection_details()
    progress = progress_mapping()
    sectors_det = sectors_data()
    ma_schema = StartupMLSchema()
    csv_path = convert_excel_to_csv(startup_path, False)

    input = csv.DictReader(open(csv_path))
    for i in input:
        i = dict(i)
        del i['']
        i["progress"] = [ progress[ele.strip()] for ele in i["progress"].split(',') ]
        i["sectors"] = [ sectors_det[j.strip()] for j in i["sectors"].split(',') if j != ""]

        if i["co_founders"] == "":
            i["co_founders"] = []
        else:
            i["co_founders"] = list(ast.literal_eval(i["co_founders"]))

        if i["num_team_members"] == "":
            i["num_team_members"] = 0
        else:
            i["num_team_members"] = int(float(i["num_team_members"]))

        round_size = round_def(int(i["round_size"]))
        i["raised"] = int(float(i["raised"]))
        i["email_confirmed"] = True
        i["approved"] = True


        email = i["email"]
        users_count = collection.estimated_document_count()
        if users_count == 0:
            _id = 0
        else:
            _id = (((users_count - 1) * 100) + 100)

        str_obj = Startup(**i)
        str_obj.save()

        str_obj = Startup.objects.filter(email=email).first()
        resp = ma_schema.dump(str_obj)
        resp["_id"] = _id
        resp["deals"] = [round_size]
        collection.insert_one(resp)
    print("All data inserted into startup and user startup successfully!")


def db_connection_details():
    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.users
    return collection


def progress_mapping():
    return  {
        "Mockups/Renderings": "mockups",
        "Prototype/Pre-Launch": "prototype",
        "Launched": "product",
        "Idea/Sketches": "mockups",
        "Beta Launched": "beta" ,
        "Taking Preorders": "preorders",
        "Product Launched": "product",
        "Team Built": "team",
        "Early Users Acquired": "users",
        "Early Revenue Generated": "revenue"
    }


def round_def(number):
    if 0 <= number <= 10000:
        return "0"
    elif 10000 <= number <= 25000:
        return "10"
    elif 25000 <= number <= 50000:
        return "25"
    elif 50000 <= number <= 100000:
        return "50"
    elif 100000 <= number <= 250000:
        return "100"
    elif 250000 <= number <= 500000:
        return "250"
    elif number > 500000:
        return "500"


def convert_excel_to_csv(file_path, is_investor):
    if is_investor:
        file_name = "investor"
    else:
        file_name = "startup"
    path = f"/Users/farhaan/Downloads/AngelFund/new_data/{file_name}.csv"
    excel_file = pd.read_excel(file_path)
    excel_file.to_csv(path)
    return path


def sectors_data():
    return {'Agriculture / Agtech': 'agtech',
            'Artifitial Intelligence': 'ai',
            'Augmented Reality': 'ar',
            'Biomedical': 'biomed',
            'Biotech': 'biotech',
            'Blockchain': 'blockchain',
            'Community': 'community',
            'Crowdfunding': 'crowdfund',
            'Developer Tools': 'devtools',
            'Diversity': 'diversity',
            'Drones': 'drones',
            'Education': 'education',
            'Energy': 'energy',
            'Enterprise': 'enterprise',
            'Entertainment': 'entertain',
            'Esports / Online Gaming': 'gaming',
            'Financial / Banking': 'banking',
            'Government': 'government',
            'Hardware': 'hardware',
            'Healthcare': 'health',
            'Marketplace': 'market',
            'Media / Advertising': 'media',
            'Moonshots / Hard Tech': 'hardtech',
            'Robotics': 'robotics',
            'Security': 'security',
            'Sport / Fitness': 'sport',
            'Transportation': 'transport',
            'Travel': 'travel',
            'Virtual Reality': 'vr',
            'Other': 'other'}

if __name__ == '__main__':
    startup_data("/Users/farhaan/Downloads/AngelFund/new_data/startup.xlsx")
    investor_data("/Users/farhaan/Downloads/AngelFund/new_data/investor.xlsx")