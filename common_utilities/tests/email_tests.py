#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
import sys
sys.path.append("../../")
from common_utilities.emails import (account_delete_email, connected_emails, email_confirmation,
google_email, password_reset, referral_email, wait_list_email_inv, wait_list_email_str)


#<==================================================================================================>
#                               EMAIL SENDING USING THREADING
#<==================================================================================================>
def send_email_threading(email, name):
    link = "https://www.google.com"
    all_info = {}
    all_info["inv_fn"] = "Farhaan"
    all_info["str_fn"] = "AngelFund"
    all_info["str_founders"] = "Birna"
    all_info["str_bio"] = "Test Bio"
    all_info["str_seeking"] = "300000"

    google_email.google_email_confirmation(email)
    # delete_user_account(email)
    # wait_list_user_inv(email, name)
    # wait_list_user_str(email, name, "Angelfund")
    # password_reset_email(email, link)
    # email_confirmation(email, link, name)
    # email_connected(email, "patel.farhaaan@gmail.com", all_info)
    # email_referral(email, "Farhaan Patel", "Farhaan", link, "investor")


#<==================================================================================================>
#                                       MAIN FUNCTION
#<==================================================================================================>
# send_email_threading("liya@angelfund.ai", "Liya")
# send_email_threading("farhaan@angelfund.ai", "Farhaan")
# send_email_threading("briandam26@yahoo.com", "Birna")
send_email_threading("birna@angelfund.ai", "Birna")
send_email_threading("liyajin7@gmail.com", "Birna")