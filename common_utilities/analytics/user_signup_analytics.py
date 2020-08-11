#<==================================================================================================>
#                                      IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from common_utilities.analytics.new_user_count_analytics import (str_daily_new_users_count,
                                                                 str_weekly_new_users_count,
                                                                 str_monthly_new_users_count,
                                                                 inv_monthly_new_users_count,
                                                                 inv_weekly_new_users_count,
                                                                 inv_daily_new_users_count)

# <==================================================================================================>
#                                   GENERAL HELPER FUCNTION
# <==================================================================================================>
def signup_analytics(is_inv):
    if is_inv:
        user_count_analytics = [inv_daily_new_users_count, inv_weekly_new_users_count, inv_monthly_new_users_count]
        for inv_cnt_func in user_count_analytics:
            inv_cnt_func()
    else:
        user_count_analytics = [str_daily_new_users_count, str_weekly_new_users_count, str_monthly_new_users_count]
        for str_cnt_func in user_count_analytics:
            str_cnt_func()