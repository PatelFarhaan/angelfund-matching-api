from project import ma
from flask_marshmallow import fields as fd


class InvestorUserSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "email", "sectors", "deals", "profile_pic_link",
                  "bio", "location", "accreditation", "syndicate", "angel", "prior_investments",
                  "email_confirmed", "approved", "first_dashboard_visit")


class InvestorMLSchema(ma.Schema):
    class Meta:
        fields = ("bio", "deals", "sectors", "angel", "syndicate", "location", "password", "referred_to",
                  "referred_by", "accreditation", "profile_pic_link", "password_reset_meta_data", "approved",
                  "last_name", "first_name", "is_logged_in", "email_confirmed", "is_google_signup", "email",
                  "first_dashboard_visit", "created", "investor", "show_profile", "monday_notifications", "show_limit",
                  "matched_week", "prior_investments", "connected", "passed", "pending", "delete_account", "count_invited",
                  "count_passed", "invite_accepted_notify", "all_transaction_fields")


class InvestorDashboardSchema(ma.Schema):
    class Meta:
        fields = ("profile_pic_link", "first_name", "last_name", "bio", "prior_investments", "sectors", "location", "deals", "syndicate")


class InvestorConnectedSchema(ma.Schema):
    action = fd.fields.String(default="Invite Sent")
    status = fd.fields.String(default="Connected")

    class Meta:
        fields = ("location", "deals", "first_name", "last_name", "profile_pic_link")


class InvestorFeedbackSchema(ma.Schema):
    action = fd.fields.String(default="Passed")

    class Meta:
        fields = ("location", "deals", "first_name", "last_name", "profile_pic_link")