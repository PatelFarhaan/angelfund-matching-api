#<==================================================================================================>
#                                          IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../")
from _datetime import datetime, timedelta, date
from project.models import (InvDailyNewUsers, InvWeeklyNewUsers, InvMonthlyNewUsers,
                            StrDailyNewUsers, StrWeeklyNewUsers, StrMonthlyNewUsers)


# <==================================================================================================>
#                                   GENERAL HELPER FUCNTION
# <==================================================================================================>
def helper(day: int, collection: (InvMonthlyNewUsers, InvWeeklyNewUsers, InvDailyNewUsers,
                                               StrMonthlyNewUsers, StrWeeklyNewUsers, StrDailyNewUsers)):
    user_obj = collection.objects.filter(date=date.today()).first()
    if user_obj:
        if datetime.now() > user_obj.current_dt + timedelta(days=day):
            new_obj = collection(count=1, date=date.today(), current_dt=datetime.now())
            new_obj.save()
        else:
            user_obj.count += 1
            user_obj.save()
    else:
        new_user = collection(count=1, date=date.today(), current_dt=datetime.now())
        new_user.save()

#<==================================================================================================>
#                                         DAILY NEW USERS
#<==================================================================================================>
def inv_daily_new_users_count():
    helper(1, InvDailyNewUsers)


def str_daily_new_users_count():
    helper(1, StrDailyNewUsers)


#<==================================================================================================>
#                                         DAILY NEW USERS
#<==================================================================================================>
def inv_weekly_new_users_count():
    helper(7, InvWeeklyNewUsers)


def str_weekly_new_users_count():
    helper(7, StrWeeklyNewUsers)


#<==================================================================================================>
#                                         DAILY NEW USERS
#<==================================================================================================>
def inv_monthly_new_users_count():
    helper(30, InvMonthlyNewUsers)


def str_monthly_new_users_count():
    helper(30, StrMonthlyNewUsers)


