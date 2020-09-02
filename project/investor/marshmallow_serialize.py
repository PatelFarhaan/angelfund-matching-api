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