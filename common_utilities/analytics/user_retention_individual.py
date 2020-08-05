#<==================================================================================================>
#                                      IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from project.models import UserAnalytics
from datetime import datetime, timedelta


#<==================================================================================================>
#                                     USER LOGIN DATA PROCESSING
#<==================================================================================================>
def individual_user_retention(email: str, is_inv: bool):
    user_obj = UserAnalytics.objects.filter(email=email, is_inv=is_inv).first()
    if user_obj:
        user_created_dt = getattr(user_obj, "current_dt")
        if user_created_dt >= datetime.now() + timedelta(days=30):
            setattr(user_obj, "third_week", [])
            setattr(user_obj, "fourth_week", [])
            setattr(user_obj, "second_week", [])
            setattr(user_obj, "today", [datetime.now()])
            setattr(user_obj, "current_dt", datetime.now())
            setattr(user_obj, "first_week", [datetime.now()])
            user_obj.save()
        else:
            current_dt = getattr(user_obj, "current_dt")
            last_login = list(getattr(user_obj, "today"))[-1]
            current_start_day = datetime.now().replace(hour=0, minute=0,
                                                       second=0, microsecond=0)
            if last_login <= current_start_day:
                setattr(user_obj, "today", [datetime.now()])
            else:
                today = list(getattr(user_obj, "today"))
                today.append(datetime.now())
                setattr(user_obj, "today", today)

            if current_dt <= datetime.now() < current_dt + timedelta(days=7):
                first_week = list(getattr(user_obj, "first_week"))
                first_week.append(datetime.now())
                setattr(user_obj, "first_week", first_week)

            if current_dt + timedelta(days=7) <= datetime.now() < current_dt + timedelta(days=14):
                second_week = list(getattr(user_obj, "second_week"))
                second_week.append(datetime.now())
                setattr(user_obj, "second_week", second_week)

            if current_dt + timedelta(days=14) <= datetime.now() < current_dt + timedelta(days=21):
                third_week = list(getattr(user_obj, "third_week"))
                third_week.append(datetime.now())
                setattr(user_obj, "third_week", third_week)

            if current_dt + timedelta(days=21) <= datetime.now() < current_dt + timedelta(days=28):
                fourth_week = list(getattr(user_obj, "fourth_week"))
                fourth_week.append(datetime.now())
                setattr(user_obj, "fourth_week", fourth_week)

            user_obj.save()
    else:
        new_users_schema = {
            "email": email,
            "third_week": [],
            "is_inv": is_inv,
            "second_week": [],
            "fourth_week": [],
            "today": [datetime.now()],
            "current_dt": datetime.now(),
            "first_week": [datetime.now()]
        }
        new_user = UserAnalytics(**new_users_schema)
        new_user.save()