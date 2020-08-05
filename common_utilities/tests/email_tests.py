#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
import sys

sys.path.append("../../")


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
# send_email_threading("birna@angelfund.ai", "Birna")