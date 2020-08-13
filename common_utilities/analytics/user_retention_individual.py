#<==================================================================================================>
#                                      IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from datetime import datetime, timedelta, date
from project.models import InvestorUserAnalytics, StartupUserAnalytics


#<==================================================================================================>
#                              INDIVIDUAL USER RETENTION FUNCTION
#<==================================================================================================>
def individual_user_retention(email: str, is_inv: bool):
    collection = InvestorUserAnalytics if is_inv else StartupUserAnalytics
    collection_obj = InvestorUserAnalytics.objects.filter(email=email).first()
    if collection_obj:
        collection_obj = collection_obj[0]

        if collection_obj.last_login.date() == date.today():
            return
        else:
            collection_obj.last_login = datetime.now()
            collection_obj.daily += [{"date": str(date.today())}]
            collection_obj.weekly = helper(collection_obj.weekly, 7)
            collection_obj.monthly = helper(collection_obj.monthly, 30)
            return
    else:
        user_obj = {}
        user_obj["daily"] = [{"date": str(date.today())}]
        user_obj["weekly"] = [{"date": str(date.today())}]
        user_obj["monthly"] = [{"date": str(date.today())}]
        user_obj["last_login"] = datetime.now()
        user_obj["email"] = email
        new_obj = collection(**user_obj)
        new_obj.save()
        return


#<==================================================================================================>
#                                      HELPER FUNCTION
#<==================================================================================================>
def helper(list_obj, days):
    last_ele_date = list_obj[-1].get("date")
    if date.today() + timedelta(days=days) >= last_ele_date:
        list_obj += [{"date": str(date.today())}]
    return list_obj