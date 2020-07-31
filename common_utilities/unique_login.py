#<==================================================================================================>
#                                      IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../")
from datetime import datetime, timedelta, date
from project.models import (InvUniqueUsersDaily, StrUniqueUsersDaily, InvUniqueUsersMonthly,
                           StrUniqueUsersMonthly)


#<==================================================================================================>
#                                  DAILY UNIQUE USER
#<==================================================================================================>
def inv_unique_users_daily(email: str):
    email = email.replace(".", "-")
    helper(email, 1, InvUniqueUsersDaily)


def str_unique_users_daily(email: str):
    email = email.replace(".", "-")
    helper(email, 1, StrUniqueUsersDaily)


# <==================================================================================================>
#                                    MONTHLY UNIQUE USER
# <==================================================================================================>
def inv_unique_users_monthly(email: str):
    email = email.replace(".", "-")
    helper(email, 30, InvUniqueUsersMonthly)


def str_unique_users_monthly(email: str):
    email = email.replace(".", "-")
    helper(email, 30, StrUniqueUsersMonthly)


# <==================================================================================================>
#                                   GENERAL HELPER FUCNTION
# <==================================================================================================>
def helper(email : str, day: int, collection: (InvUniqueUsersMonthly,StrUniqueUsersDaily)):
    user_obj = collection.objects.filter(date=date.today()).first()
    if user_obj:
        if datetime.now() > user_obj.current_dt + timedelta(days=day):
            new_obj = collection(count=1, date=date.today(),
                                          users_dict={email: True}, current_dt=datetime.now())
            new_obj.save()
        else:
            temp_dict = dict(user_obj.users_dict)
            temp_dict[email] = True
            user_obj.users_dict = temp_dict
            user_obj.count = len(temp_dict)
            user_obj.save()
    else:
        new_dict = dict()
        new_dict[email] = True
        new_user = collection(count=1, date=date.today(),
                                       users_dict=new_dict, current_dt=datetime.now())
        new_user.save()