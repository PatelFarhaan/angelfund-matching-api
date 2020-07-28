#<==================================================================================================>
#                                      IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../")
from project.models import UserAnalytics
from _datetime import datetime, timedelta


#<==================================================================================================>
#                                     USER LOGIN DATA PROCESSING
#<==================================================================================================>
def user_login_data_processing(email: str, is_inv: bool):
    """
    This function processes login data of a user for analytics for admin panel.

    :param email:    email address of the user
    :param is_inv:   whether the user is investor or startup
    :return:         None
    """

    user_obj = UserAnalytics.objects.filter(email=email, is_inv=is_inv).first()
    if user_obj:
        today = list(getattr(user_obj, "today"))
        first_week = list(getattr(user_obj, "first_week"))
        today.append(datetime.now())
        first_week.append(datetime.now())
        user_obj.today = today
        user_obj.first_week = first_week
        user_obj.save()
        data_preprocessing(user_obj)
    else:
        new_users_schema = {
            "email": email,
            "third_week": [],
            "is_inv": is_inv,
            "second_week": [],
            "fourth_week": [],
            "today": [datetime.now()],
            "first_week": [datetime.now()]
        }
        new_user = UserAnalytics(**new_users_schema)
        new_user.save()


#<==================================================================================================>
#                                    USER LOGIN DATA PREPROCESSING
#<==================================================================================================>
def data_preprocessing(user_obj: UserAnalytics):
    """
    This function filters all the datetime object in the list which are past 30 days

    :param user_obj:   UserAnalytics object of a user
    :return:           None
    """

    def helper(arr: list, user_obj: UserAnalytics) -> list:
        if not arr:
            return []

        current_dt = datetime.now()
        target_dt = datetime.now() - timedelta(days=30)
        fourth_week = datetime.now() - timedelta(days=7)
        first_week = timedelta(days=28) - timedelta(days=21)
        third_week = timedelta(days=21) - timedelta(days=14)
        second_week = timedelta(days=14) - timedelta(days=7)

        for index, dt_obj in enumerate(arr):
            if dt_obj < target_dt:
                arr.pop(index)

            elif first_week <= dt_obj < second_week:
                first_week_obj = list(user_obj.first_week)
                first_week_obj.append(dt_obj)
                setattr(user_obj, "first_week", first_week_obj)
                user_obj.save()
                arr.pop(index)

            elif second_week <= dt_obj < third_week:
                second_week_obj = list(user_obj.second_week)
                second_week_obj.append(dt_obj)
                setattr(user_obj, "second_week", second_week_obj)
                user_obj.save()
                arr.pop(index)

            elif third_week <= dt_obj < fourth_week:
                third_week_obj = list(user_obj.third_week)
                third_week_obj.append(dt_obj)
                setattr(user_obj, "third_week", third_week_obj)
                user_obj.save()
                arr.pop(index)

            elif fourth_week <= dt_obj < current_dt:
                fourth_week_obj = list(user_obj.fourth_week)
                fourth_week_obj.append(dt_obj)
                setattr(user_obj, "fourth_week", fourth_week_obj)
                user_obj.save()
                arr.pop(index)
        return arr

    today = list(user_obj.today)
    third_week = list(user_obj.third_week)
    first_week = list(user_obj.first_week)
    second_week = list(user_obj.second_week)
    fourth_week = list(user_obj.fourth_week)

    user_obj.today = helper(today, user_obj)
    user_obj.first_week = helper(first_week, user_obj)
    user_obj.third_week = helper(third_week, user_obj)
    user_obj.second_week = helper(second_week, user_obj)
    user_obj.fourth_week = helper(fourth_week, user_obj)
    user_obj.save()