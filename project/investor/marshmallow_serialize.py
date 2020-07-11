#<==================================================================================================>
#                                     IMPORTS
#<==================================================================================================>
from project import ma
from flask_marshmallow import fields as fd


#<==================================================================================================>
#                                     INVESTOR USER SCHEMA
#<==================================================================================================>
class InvestorUserSchema(ma.Schema):
    id = fd.fields.String()

    class Meta:
        fields = ("first_name", "last_name", "id", "sectors", "deals", "profile_pic_link",
                  "bio", "location", "accreditation", "syndicate", "angel", "prior_investments",
                  "email_confirmed", "approved", "first_dashboard_visit", "monday_notification",
                  "show_profile", "first_invite")


#<==================================================================================================>
#                                     INVESTOR ML SCHEMA
#<==================================================================================================>
class InvestorMLSchema(ma.Schema):
    class Meta:
        fields = ("count_invited", "count_passed", "invite_accepted_notify", "all_transaction_fields",
                  "first_dashboard_visit", "created", "investor", "show_profile", "monday_notifications",
                  "profile_pic_link", "password_reset_meta_data", "approved", "first_invite", "last_name",
                  "matched_week", "prior_investments", "connected", "passed", "pending", "delete_account",
                  "bio", "deals", "sectors", "angel", "syndicate", "location", "password", "accreditation",
                  "first_name", "is_logged_in", "email_confirmed", "is_google_signup", "email", "show_limit")


#<==================================================================================================>
#                                     INVESTOR DASHBOARD SCHEMA
#<==================================================================================================>
class InvestorDashboardSchema(ma.Schema):
    id = fd.fields.String()

    class Meta:
        fields = ("profile_pic_link", "first_name", "last_name", "bio", "prior_investments", "sectors", "location",
                  "deals", "syndicate", "id")


#<==================================================================================================>
#                                     INVESTOR CONNECTED SCHEMA
#<==================================================================================================>
class InvestorConnectedSchema(ma.Schema):
    action = fd.fields.String(default="Invite Sent")
    status = fd.fields.String(default="Connected")
    id = fd.fields.String()

    class Meta:
        fields = ("location", "deals", "first_name", "last_name", "profile_pic_link", "action", "status", "id")


#<==================================================================================================>
#                                     INVESTOR FEEDBACK SCHEMA
#<==================================================================================================>
class InvestorFeedbackSchema(ma.Schema):
    action = fd.fields.String(default="Passed")

    class Meta:
        fields = ("location", "deals", "first_name", "last_name", "profile_pic_link", "action")