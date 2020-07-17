#<==================================================================================================>
#                                     IMPORTS
#<==================================================================================================>
from project import ma
from flask_marshmallow import fields as fd


#<==================================================================================================>
#                                     STARTUP USER SCHEMA
#<==================================================================================================>
class StartupUserSchema(ma.Schema):
    id = fd.fields.String()

    class Meta:
        fields = ("first_name", "last_name", "id", "location", "profile_pic_link",
                  "sectors", "company_name", "company_link", "startup_pitch", "first_invite",
                  "bio", "round_size", "raised", "progress", "position", "co_founders",
                  "num_team_members", "slide_deck", "approved", "email_confirmed",
                  "first_dashboard_visit", "show_profile", "monday_notification")


#<==================================================================================================>
#                                  STARTUP DASHBOARD SCHEMA
#<==================================================================================================>
class StartupDashboardSchema(ma.Schema):
    id = fd.fields.String()

    class Meta:
        fields = ("bio", "raised", "sectors", "location", "id", "progress", "round_size",
                  "slide_deck", "co_founders", "company_link", "profile_pic_link", "company_name")


#<==================================================================================================>
#                                     STARTUP CONNECTED SCHEMA
#<==================================================================================================>
class StartupConnectedSchema(ma.Schema):
    action = fd.fields.String(default="Invite Sent")
    status = fd.fields.String(default="Connected")
    id = fd.fields.String()

    class Meta:
        fields = ("location", "round_size", "company_name", "profile_pic_link", "action", "status", "id")


#<==================================================================================================>
#                                     STARTUP PASSED SCHEMA
#<==================================================================================================>
class StartupPassedSchema(ma.Schema):
    status = fd.fields.String(default="Revisit Deal")
    action = fd.fields.String(default="Passed")
    id = fd.fields.String()

    class Meta:
        fields = ("location", "round_size", "company_name", "profile_pic_link", "action", "status", "id")


#<==================================================================================================>
#                                     STARTUP ML SCHEMA
#<==================================================================================================>
class StartupMLSchema(ma.Schema):
    class Meta:
        fields = ("slide_deck", "round_size", "company_link", "company_name", "num_team_members",
                  "last_name", "first_name", "is_logged_in", "email_confirmed", "is_google_signup", "email",
                  "bio", "sectors", "raised", "progress", "position", "password", "location", "first_invite",
                  "count_invited", "count_passed", "show_limit", "invite_accepted_notify", "all_transaction_fields",
                  "first_dashboard_visit", "created", "investor", "feedback", "connected", "passed", "matched_week",
                  "startup_pitch", "profile_pic_link", "raised_capital_desc", "password_reset_meta_data", "approved",
                  "pending", "co_founders", "show_slide_deck", "delete_account", "show_profile", "monday_notification",
                  "deals")