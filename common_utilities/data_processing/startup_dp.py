#<==================================================================================================>
#                                       IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from project.models import Startup, Investor
from project.startup.marshmallow_serialize import StartupDashboardSchema


#<==================================================================================================>
#                                PROCESSING HELPER
#<==================================================================================================>
def processing_helper(email: str) -> dict:
    str_obj = Startup.objects.filter(email=email).first()

    if not str_obj or not str_obj.show_profile or not str_obj.approved:
        return {"result": False, "data": None}

    ma_schema = StartupDashboardSchema()
    res = ma_schema.dump(str_obj)
    return {"result": True, "data": res}


#<==================================================================================================>
#                              PROCESS ALL STARTUP DATA
#<==================================================================================================>
def get_all_startup_data(data: list, inv_obj: Investor) -> list:
    res = []
    current_count = 0
    data = list(set(data))
    total_count = inv_obj.show_limit
    all_transactional_data = inv_obj.all_transaction_fields

    for str_email in data:
        if not str_email in all_transactional_data:
            str_details = processing_helper(str_email)
            if str_details["result"]:
                res.append(str_details["data"])
                current_count += 1
                if current_count == total_count:
                    return res
    return res


#<==================================================================================================>
#                              REMOVE DATA FROM DISCOVER CARDS
#<==================================================================================================>
def remove_data_from_discover(inv_obj: Investor, email: str):
    _cards = inv_obj.discover_cards
    if email in _cards:
        _cards.remove(email)
        inv_obj.discover_cards = _cards
        inv_obj.total_transaction_this_week += 1
        inv_obj.save()
        return