#<==================================================================================================>
#                                       IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from project.models import Investor
from project.investor.marshmallow_serialize import InvestorDashboardSchema


#<==================================================================================================>
#                                PROCESSING HELPER
#<==================================================================================================>
def processing_helper(email: str) -> dict:
    inv_obj = Investor.objects.filter(email=email).first()
    if not inv_obj:
        return {"result": False, "data": None}

    ma_schema = InvestorDashboardSchema()
    res = ma_schema.dump(inv_obj)
    return {"result": True, "data": res}


#<==================================================================================================>
#                              PROCESS ALL INVESTOR DATA
#<==================================================================================================>
def get_all_investor_data(data: list) -> list:
    res = []
    data = list(set(data))

    for inv_email in data:
        inv_details = processing_helper(inv_email)
        if inv_details["result"]:
            res.append(inv_details["data"])
    return res