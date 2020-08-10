#<==================================================================================================>
#                                      IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from datetime import datetime, timedelta
from project.models import (InvUniqueUsersDaily, StrUniqueUsersDaily, InvUniqueUsersMonthly,
                            StrUniqueUsersMonthly, InvUniqueUsersWeekly, StrUniqueUsersWeekly)


# <==================================================================================================>
#                                   GENERAL HELPER FUCNTION
# <==================================================================================================>
def helper(email: str, day: int, collection: (InvUniqueUsersMonthly,StrUniqueUsersDaily)):
    def untrue_current():
        current_obj = collection.objects.filter(current=True).first()
        if current_obj:
            current_obj.current = False
            current_obj.save()

    user_obj = collection.objects.filter(current=True).first()
    if user_obj:
        if datetime.now() > user_obj.current_dt + timedelta(days=day):
            untrue_current()
            current_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            new_obj = collection(count=1, current=True, users_dict={email: True},
                                 current_dt=current_day)
            new_obj.save()
        else:
            temp_dict = dict(user_obj.users_dict)
            temp_dict[email] = True
            user_obj.users_dict = temp_dict
            user_obj.count = len(temp_dict)
            user_obj.save()
    else:
        untrue_current()
        new_dict = dict()
        new_dict[email] = True
        current_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        new_user = collection(count=1, current=True, users_dict=new_dict,
                              current_dt=current_day)
        new_user.save()


#<==================================================================================================>
#                                  DAILY UNIQUE USER
#<==================================================================================================>
def inv_unique_users_daily(email: str):
    email = email.replace(".", "-")
    helper(email, 1, InvUniqueUsersDaily)


def str_unique_users_daily(email: str):
    email = email.replace(".", "-")
    helper(email, 1, StrUniqueUsersDaily)


#<==================================================================================================>
#                                  WEEKLY UNIQUE USER
#<==================================================================================================>
def inv_unique_users_weekly(email: str):
    email = email.replace(".", "-")
    helper(email, 7, InvUniqueUsersWeekly)


def str_unique_users_weekly(email: str):
    email = email.replace(".", "-")
    helper(email, 7, StrUniqueUsersWeekly)


# <==================================================================================================>
#                                    MONTHLY UNIQUE USER
# <==================================================================================================>
def inv_unique_users_monthly(email: str):
    email = email.replace(".", "-")
    helper(email, 30, InvUniqueUsersMonthly)


def str_unique_users_monthly(email: str):
    email = email.replace(".", "-")
    helper(email, 30, StrUniqueUsersMonthly)