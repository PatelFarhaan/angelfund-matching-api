#<==================================================================================================>
#                                          IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from _datetime import datetime, timedelta, date
from project.models import (InvUniqueUsersDaily, InvUniqueUsersWeekly, InvUniqueUsersMonthly,
                            StrUniqueUsersDaily, StrUniqueUsersWeekly, StrUniqueUsersMonthly,
                            InvRetention, StrRetention)


# <==================================================================================================>
#                                   GENERAL HELPER FUCNTION
# <==================================================================================================>
def helper(days: int, collection: (InvRetention, StrRetention),
           daily_unique_model: (InvUniqueUsersDaily, StrUniqueUsersDaily),
           weekly_unique_model: (InvUniqueUsersWeekly, StrUniqueUsersWeekly),
           monthly_unique_model: (InvUniqueUsersMonthly, StrUniqueUsersMonthly)):

    def days_check(days, retention_list, model):
        last_retention = retention_list[-1]
        unique_login_cnt = model.objects.filter(current=True).first()
        last_retention_date = datetime.strptime(last_retention.get("date"), '%Y-%m-%d').date()
        if date.today() >= last_retention_date + timedelta(days=days):
            obj = {"date": str(date.today()),
                   "unique_login": unique_login_cnt.count if unique_login_cnt else 0}
            retention_list.append(obj)
            return retention_list
        else:
            unique_login_cnt = unique_login_cnt.count if unique_login_cnt else 0
            last_retention["unique_login"] = unique_login_cnt
            return retention_list

    collection_obj = collection.objects.all()
    if collection_obj:
        collection_obj = collection_obj[0]
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
        daily_current = daily_unique_model.objects.filter(current=True).first()
        weekly_current = weekly_unique_model.objects.filter(current=True).first()
        monthly_current = monthly_unique_model.objects.filter(current=True).first()

        new_obj = collection(daily=[{"date": str(date.today()),
                                     "unique_login": daily_current.count if daily_current else 0}],
                             weekly=[{"date": str(date.today()),
                                      "unique_login": weekly_current.count if weekly_current else 0}],
                             monthly=[{"date": str(date.today()),
                                       "unique_login": monthly_current.count if monthly_current else 0}])
        new_obj.save()


#<==================================================================================================>
#                                         DAILY RETENTION
#<==================================================================================================>
def inv_daily_retention():
    helper(1, InvRetention, InvUniqueUsersDaily, InvUniqueUsersWeekly, InvUniqueUsersMonthly)


def str_daily_retention():
    helper(1, StrRetention, StrUniqueUsersDaily, StrUniqueUsersWeekly, StrUniqueUsersMonthly)

#<==================================================================================================>
#                                         WEEKLY RETENTION
#<==================================================================================================>
def inv_weekly_retention():
    helper(7, InvRetention, InvUniqueUsersDaily, InvUniqueUsersWeekly, InvUniqueUsersMonthly)


def str_weekly_retention():
    helper(7, StrRetention, StrUniqueUsersDaily, StrUniqueUsersWeekly, StrUniqueUsersMonthly)


#<==================================================================================================>
#                                         MONTHLY RETENTION
#<==================================================================================================>
def inv_monthly_retention():
    helper(30, InvRetention, InvUniqueUsersDaily, InvUniqueUsersWeekly, InvUniqueUsersMonthly)


def str_monthly_retention():
    helper(30, StrRetention, StrUniqueUsersDaily, StrUniqueUsersWeekly, StrUniqueUsersMonthly)