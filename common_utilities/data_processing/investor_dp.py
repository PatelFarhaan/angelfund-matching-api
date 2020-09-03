#<==================================================================================================>
#                                       IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from project.models import Investor, Startup
from project.investor.marshmallow_serialize import InvestorDashboardSchema


#<==================================================================================================>
#                                PROCESSING HELPER
#<==================================================================================================>
def processing_helper(email: str) -> dict:
    inv_obj = Investor.objects.filter(email=email).first()

    if not inv_obj or not inv_obj.show_profile or not inv_obj.approved:
        return {"result": False, "data": None}

    ma_schema = InvestorDashboardSchema()
    res = ma_schema.dump(inv_obj)
    return {"result": True, "data": res}


#<==================================================================================================>
#                              PROCESS ALL INVESTOR DATA
#<==================================================================================================>
def get_all_investor_data(data: list, str_obj: Startup) -> list:
    res = []
    current_count = 0
    data = list(set(data))
    all_transactional_data = str_obj.all_transaction_fields
    total_count = str_obj.show_limit - str_obj.total_transaction_this_week

    for inv_email in data:
        if not inv_email in all_transactional_data:
            inv_details = processing_helper(inv_email)
            if inv_details["result"]:
                res.append(inv_details["data"])
                current_count += 1
                if current_count == total_count:
                    return res
    return res


#<==================================================================================================>
#                              REMOVE DATA FROM DISCOVER CARDS
#<==================================================================================================>
def remove_data_from_discover(str_obj: Startup, email: str):
    _cards = str_obj.discover_cards
    if email in _cards:
        _cards.remove(email)
        str_obj.discover_cards = _cards
        str_obj.total_transaction_this_week += 1
        str_obj.save()
        return