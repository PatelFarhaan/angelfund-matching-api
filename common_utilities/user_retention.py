#<==================================================================================================>
#                                          IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../")
from _datetime import datetime, timedelta, date
from project.models import (InvUniqueUsersDaily, InvUniqueUsersWeekly, InvUniqueUsersMonthly,
                            StrUniqueUsersDaily, StrUniqueUsersWeekly, StrUniqueUsersMonthly,
                            InvRetention, StrRetention, Investor, Startup)


# <==================================================================================================>
#                                   GENERAL HELPER FUCNTION
# <==================================================================================================>
def helper(days: int, collection: (InvRetention, StrRetention), user_model: (Investor, Startup),
           daily_unique_model: (InvUniqueUsersDaily, StrUniqueUsersDaily),
           weekly_unique_model: (InvUniqueUsersWeekly, StrUniqueUsersWeekly),
           monthly_unique_model: (InvUniqueUsersMonthly, StrUniqueUsersMonthly)):

    def retention_calculate(previous, current):
        return (current/previous) * 100

    def days_check(days, retention_list, model):
        last_retention = retention_list[-1]
        user_count = model.objects.filter(current=True).first()
        if date.today() > last_retention.get("date") + (datetime.now() + timedelta(days=days)).date():
            obj = {"date": date.today(),
                   "retention_rate": retention_calculate(last_retention.get("retention_rate"),
                                                         user_count.count if user_count else 0)}
            retention_list.append(obj)
            return retention_list
        else:
            retention_rate = retention_calculate(last_retention.get("retention_rate"),
                                                         user_count.count if user_count else 0)
            last_retention["retention_rate"] = retention_rate
            return retention_list

    collection_obj = collection.objects.all()
    if collection_obj:
        if days == 1:
            daily_retention_list = list(collection_obj.daily)
            updated_daily_retention_list = days_check(days, daily_retention_list, daily_unique_model)
            collection_obj.daily = updated_daily_retention_list
            collection_obj.save()
        elif days == 7:
            weekly_retention_list = list(collection_obj.weekly)
            updated_weekly_retention_list = days_check(days, weekly_retention_list, weekly_unique_model)
            collection_obj.weekly = updated_weekly_retention_list
            collection_obj.save()
        elif days == 30:
            monthly_retention_list = list(collection_obj.monthly)
            updated_monthly_retention_list = days_check(days, monthly_retention_list, monthly_unique_model)
            collection_obj.monthly = updated_monthly_retention_list
            collection_obj.save()
    else:
        total_count = user_model.objects.count()
        daily_current = daily_unique_model.objects.filter(current=True).first()
        weekly_current = weekly_unique_model.objects.filter(current=True).first()
        monthly_current = monthly_unique_model.objects.filter(current=True).first()

        new_obj = collection(daily=[retention_calculate(daily_current.count if daily_current else 0, total_count)],
                             weekly=[retention_calculate(weekly_current.count if weekly_current else 0, total_count)],
                             monthly=[retention_calculate(monthly_current.count if monthly_current else 0, total_count)])
        new_obj.save()


#<==================================================================================================>
#                                         DAILY NEW USERS
#<==================================================================================================>
def inv_daily_new_users_count():
    helper(1, InvRetention, Investor, InvUniqueUsersDaily, InvUniqueUsersWeekly, InvUniqueUsersMonthly)

inv_daily_new_users_count()


def str_daily_new_users_count():
    helper(1, StrRetention, Startup, StrUniqueUsersDaily, StrUniqueUsersWeekly, StrUniqueUsersMonthly)


#<==================================================================================================>
#                                         DAILY NEW USERS
#<==================================================================================================>
def inv_weekly_new_users_count():
    helper(7, InvRetention, Investor, InvUniqueUsersDaily, InvUniqueUsersWeekly, InvUniqueUsersMonthly)


def str_weekly_new_users_count():
    helper(7, StrRetention, Startup, StrUniqueUsersDaily, StrUniqueUsersWeekly, StrUniqueUsersMonthly)


#<==================================================================================================>
#                                         DAILY NEW USERS
#<==================================================================================================>
def inv_monthly_new_users_count():
    helper(30, InvRetention, Investor, InvUniqueUsersDaily, InvUniqueUsersWeekly, InvUniqueUsersMonthly)


def str_monthly_new_users_count():
    helper(30, StrRetention, Startup, StrUniqueUsersDaily, StrUniqueUsersWeekly, StrUniqueUsersMonthly)

