#<==================================================================================================>
#                                      IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../")
from _datetime import datetime, timedelta
from project.models import (InvUniqueUsersDaily, StrUniqueUsersDaily, InvUniqueUsersMonthly,
                           StrUniqueUsersMonthly)


#<==================================================================================================>
#                                 MONTHLY UNIQUE USER
#<==================================================================================================>
def inv_unique_users_daily(email: str):
    email = email.replace(".", "-")

    users_obj = InvUniqueUsersDaily.objects.all()
    if users_obj:
        user_obj = users_obj[0]
        if datetime.now() > user_obj.current_dt + timedelta(days=1):
            new_obj = InvUniqueUsersDaily(count=1, users_dict={email: True}, current_dt=datetime.now())
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
        new_user = InvUniqueUsersDaily(count=1, users_dict=new_dict, current_dt=datetime.now())
        new_user.save()


def str_unique_users_daily(email: str):
    email = email.replace(".", "-")

    users_obj = StrUniqueUsersDaily.objects.all()
    if users_obj:
        user_obj = users_obj[0]
        if datetime.now() > user_obj.current_dt + timedelta(days=1):
            new_obj = StrUniqueUsersDaily(count=1, users_dict={email: True}, current_dt=datetime.now())
            new_obj.save()
        else:
            temp_dict = dict(user_obj.users_dict)
            temp_dict[email] = True
            user_obj.users_dict = temp_dict
            user_obj.count = len(temp_dict)
            user_obj.save()
    else:
        new_user = StrUniqueUsersDaily(count=1, users_dict={email: True}, current_dt=datetime.now())
        new_user.save()


# <==================================================================================================>
#                                    MONTHLY UNIQUE USER
# <==================================================================================================>
def inv_unique_users_monthly(email: str):
    email = email.replace(".", "-")

    users_obj = InvUniqueUsersMonthly.objects.all()
    if users_obj:
        user_obj = users_obj[0]
        if datetime.now() > user_obj.current_dt + timedelta(days=30):
            new_obj = InvUniqueUsersMonthly(count=1, users_dict={email: True}, current_dt=datetime.now())
            new_obj.save()
        else:
            temp_dict = dict(user_obj.users_dict)
            temp_dict[email] = True
            user_obj.users_dict = temp_dict
            user_obj.count = len(temp_dict)
            user_obj.save()
    else:
        new_user = InvUniqueUsersMonthly(count=1, users_dict={email: True}, current_dt=datetime.now())
        new_user.save()


def str_unique_users_monthly(email: str):
    email = email.replace(".", "-")

    users_obj = StrUniqueUsersMonthly.objects.all()
    if users_obj:
        user_obj = users_obj[0]
        if datetime.now() > user_obj.current_dt + timedelta(days=30):
            new_obj = StrUniqueUsersMonthly(count=1, users_dict={email: True}, current_dt=datetime.now())
            new_obj.save()
        else:
            temp_dict = dict(user_obj.users_dict)
            temp_dict[email] = True
            user_obj.users_dict = temp_dict
            user_obj.count = len(temp_dict)
            user_obj.save()
    else:
        new_user = StrUniqueUsersMonthly(count=1, users_dict={email: True}, current_dt=datetime.now())
        new_user.save()