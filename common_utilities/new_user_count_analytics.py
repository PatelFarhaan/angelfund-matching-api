#<==================================================================================================>
#                                          IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../")
from _datetime import datetime, timedelta
from project.models import DailyNewUsers, WeeklyNewUsers, MonthlyNewUsers


#<==================================================================================================>
#                                         DAILY NEW USERS
#<==================================================================================================>
def daily_new_users_count():
    dnu_obj = DailyNewUsers.objects.all()
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
        dnu_obj = DailyNewUsers(count=1, current_dt=datetime.now())
        dnu_obj.save()


#<==================================================================================================>
#                                         DAILY NEW USERS
#<==================================================================================================>
def weekly_new_users_count():
    wnu_obj = WeeklyNewUsers.objects.all()
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
        dnu_obj = WeeklyNewUsers(count=1, current_dt=datetime.now())
        dnu_obj.save()


#<==================================================================================================>
#                                         DAILY NEW USERS
#<==================================================================================================>
def monthly_new_users_count():
    mnu_obj = MonthlyNewUsers.objects.all()
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
        dnu_obj = MonthlyNewUsers(count=1, current_dt=datetime.now())
        dnu_obj.save()