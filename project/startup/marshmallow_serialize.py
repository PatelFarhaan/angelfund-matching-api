from project import ma
from flask_marshmallow import fields as fd


class StartupUserSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "email", "location",
                  "sectors", "company_name", "company_link", "startup_pitch",
                  "bio", "round_size", "raised", "progress", "position",
                  "num_team_members", "slide_deck", "approved", "email_confirmed",
                  "first_dashboard_visit")


class StartupDashboardSchema(ma.Schema):
    class Meta:
        fields = ("bio", "raised", "sectors", "location", "name", "email", "progress", "round_size",
                  "slide_deck", "co_founders", "company_link", "profile_pic_link", "company_name")


class StartupConnectedSchema(ma.Schema):
    action = fd.fields.String(default="Invite Sent")
    status = fd.fields.String(default="Connected")

    class Meta:
        fields = ("location", "round_size", "company_name", "profile_pic_link", "action")


class StartupPassedSchema(ma.Schema):
    action = fd.fields.String(default="Passed")

    class Meta:
        fields = ("location", "round_size", "company_name", "profile_pic_link", "action", "email")


class StartupMLSchema(ma.Schema):
    class Meta:
        fields = ("bio", "sectors", "raised", "progress", "position", "password", "location", "referred_to",
                  "slide_deck", "referred_by", "round_size", "company_link", "company_name", "num_team_members",
                  "startup_pitch", "profile_pic_link", "raised_capital_desc", "password_reset_meta_data", "approved",
                  "last_name", "first_name", "is_logged_in", "email_confirmed", "is_google_signup", "email",
                  "first_dashboard_visit", "created", "investor", "feedback", "connected", "passed", "matched_week",
                  "pending", "co_founders", "show_slide_deck", "delete_account", "show_profile", "monday_notification",
                  "count_invited", "count_passed", "show_limit")