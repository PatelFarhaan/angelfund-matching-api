#<==================================================================================================>
#                                       IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from project.models import Startup
from project.startup.marshmallow_serialize import StartupDashboardSchema


#<==================================================================================================>
#                                PROCESSING HELPER
#<==================================================================================================>
def processing_helper(email: str) -> dict:
    str_obj = Startup.objects.filter(email=email).first()
    if not str_obj:
        return {"result": False, "data": None}

    ma_schema = StartupDashboardSchema()
    res = ma_schema.dump(str_obj)
    return {"result": True, "data": res}


#<==================================================================================================>
#                              PROCESS ALL STARTUP DATA
#<==================================================================================================>
def get_all_startup_data(data: list) -> list:
    res = []
    data = list(set(data))

    for str_email in data:
        str_details = processing_helper(str_email)
        if str_details["result"]:
            res.append(str_details["data"])
    return res