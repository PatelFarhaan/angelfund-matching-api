#<==================================================================================================>
#                                          IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../")
from _datetime import datetime, timedelta
from project.models import (InvDailyNewUsers, InvWeeklyNewUsers, InvMonthlyNewUsers,
                            StrDailyNewUsers, StrWeeklyNewUsers, StrMonthlyNewUsers)


#<==================================================================================================>
#                                         DAILY NEW USERS
#<==================================================================================================>
def inv_daily_new_users_count():
    dnu_obj = InvDailyNewUsers.objects.all()
    if dnu_obj:
        current_obj = dnu_obj[0]
        if datetime.now() > current_obj.current_dt + timedelta(days=1):
            current_obj.current_dt = datetime.now()
            current_obj.count = 1
            current_obj.save()
        else:
            current_obj.count += 1
            current_obj.save()
    else:
        dnu_obj = InvDailyNewUsers(count=1, current_dt=datetime.now())
        dnu_obj.save()


def str_daily_new_users_count():
    dnu_obj = StrDailyNewUsers.objects.all()
    if dnu_obj:
        current_obj = dnu_obj[0]
        if datetime.now() > current_obj.current_dt + timedelta(days=1):
            current_obj.current_dt = datetime.now()
            current_obj.count = 1
            current_obj.save()
        else:
            current_obj.count += 1
            current_obj.save()
    else:
        dnu_obj = StrDailyNewUsers(count=1, current_dt=datetime.now())
        dnu_obj.save()


#<==================================================================================================>
#                                         DAILY NEW USERS
#<==================================================================================================>
def inv_weekly_new_users_count():
    wnu_obj = InvWeeklyNewUsers.objects.all()
    if wnu_obj:
        current_obj = wnu_obj[0]
        if datetime.now() > current_obj.current_dt + timedelta(days=7):
            current_obj.current_dt = datetime.now()
            current_obj.count = 1
            current_obj.save()
        else:
            current_obj.count += 1
            current_obj.save()
    else:
        dnu_obj = InvWeeklyNewUsers(count=1, current_dt=datetime.now())
        dnu_obj.save()


def str_weekly_new_users_count():
    wnu_obj = StrWeeklyNewUsers.objects.all()
    if wnu_obj:
        current_obj = wnu_obj[0]
        if datetime.now() > current_obj.current_dt + timedelta(days=7):
            current_obj.current_dt = datetime.now()
            current_obj.count = 1
            current_obj.save()
        else:
            current_obj.count += 1
            current_obj.save()
    else:
        dnu_obj = StrWeeklyNewUsers(count=1, current_dt=datetime.now())
        dnu_obj.save()


#<==================================================================================================>
#                                         DAILY NEW USERS
#<==================================================================================================>
def inv_monthly_new_users_count():
    mnu_obj = InvMonthlyNewUsers.objects.all()
    if mnu_obj:
        current_obj = mnu_obj[0]
        if datetime.now() > current_obj.current_dt + timedelta(days=30):
            current_obj.current_dt = datetime.now()
            current_obj.count = 1
            current_obj.save()
        else:
            current_obj.count += 1
            current_obj.save()
    else:
        dnu_obj = InvMonthlyNewUsers(count=1, current_dt=datetime.now())
        dnu_obj.save()


def str_monthly_new_users_count():
    mnu_obj = StrMonthlyNewUsers.objects.all()
    if mnu_obj:
        current_obj = mnu_obj[0]
        if datetime.now() > current_obj.current_dt + timedelta(days=30):
            current_obj.current_dt = datetime.now()
            current_obj.count = 1
            current_obj.save()
        else:
            current_obj.count += 1
            current_obj.save()
    else:
        dnu_obj = StrMonthlyNewUsers(count=1, current_dt=datetime.now())
        dnu_obj.save()