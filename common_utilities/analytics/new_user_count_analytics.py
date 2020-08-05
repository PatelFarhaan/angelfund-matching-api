#<==================================================================================================>
#                                          IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from _datetime import datetime, timedelta
from project.models import (InvDailyNewUsers, InvWeeklyNewUsers, InvMonthlyNewUsers,
                            StrDailyNewUsers, StrWeeklyNewUsers, StrMonthlyNewUsers)


# <==================================================================================================>
#                                   GENERAL HELPER FUCNTION
# <==================================================================================================>
def helper(day: int, collection: (InvMonthlyNewUsers, InvWeeklyNewUsers, InvDailyNewUsers,
                                  StrMonthlyNewUsers, StrWeeklyNewUsers, StrDailyNewUsers)):
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
            new_obj = collection(count=1, current=True, current_dt=current_day)
            new_obj.save()
        else:
            user_obj.count += 1
            user_obj.save()
    else:
        untrue_current()
        current_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        new_user = collection(count=1, current=True, current_dt=current_day)
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


