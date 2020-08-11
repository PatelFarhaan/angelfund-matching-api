#<==================================================================================================>
#                                      IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from common_utilities.analytics.user_retention_individual import individual_user_retention
from common_utilities.analytics.user_retention import (inv_daily_retention, inv_weekly_retention,
                                                       inv_monthly_retention, str_monthly_retention,
                                                       str_daily_retention, str_weekly_retention)
from common_utilities.analytics.unique_login import (inv_unique_users_weekly, inv_unique_users_daily,
                                                     inv_unique_users_monthly, str_unique_users_daily,
                                                     str_unique_users_monthly, str_unique_users_weekly)


# <==================================================================================================>
#                                   GENERAL HELPER FUCNTION
# <==================================================================================================>
def login_analytics(email, is_inv):
    if is_inv:
        unique_user_list = [inv_unique_users_daily, inv_unique_users_weekly, inv_unique_users_monthly]
        for inv_unique_function in unique_user_list:
            inv_unique_function(email)

        user_retention_list = [inv_daily_retention, inv_weekly_retention, inv_monthly_retention]
        for inv_retention_modules in user_retention_list:
            inv_retention_modules()

    else:
        unique_user_list = [str_unique_users_daily, str_unique_users_weekly, str_unique_users_monthly]
        for str_unique_function in unique_user_list:
            str_unique_function(email)

        user_retention_list = [str_daily_retention, str_weekly_retention, str_monthly_retention]
        for str_retention_modules in user_retention_list:
            str_retention_modules()

    individual_user_retention(email, is_inv)