from project import ma
from flask_marshmallow import fields as fd


class StartupUserSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "email", "location",
                  "sectors", "company_name", "company_link", "startup_pitch",
                  "bio", "round_size", "raised", "progress", "position",
                  "num_team_members", "slide_deck", "approved", "email_confirmed",
                  "first_dashboard_visit")


class StartupMLSchema(ma.Schema):
    class Meta:
        fields = ("email", "sectors", "deals", "investor", "show_profile", "show_limit",
                  "matched_week", "count_invited", "count_passed", "bio", "accreditation",
                  "syndicate")


class StartupDashboardSchema(ma.Schema):
    class Meta:
        fields = ("bio", "raised", "sectors", "location", "name", "email", "progress", "round_size",
                  "slide_deck", "company_link", "co_founders", "profile_pic_link", "company_name")


class StartupConnectedSchema(ma.Schema):
    action = fd.fields.String(default="Invite Sent")
    status = fd.fields.String(default="Connected")

    class Meta:
        fields = ("location", "round_size", "company_name", "profile_pic_link", "action")


class StartupPassedSchema(ma.Schema):
    action = fd.fields.String(default="Passed")

    class Meta:
        fields = ("location", "round_size", "company_name", "profile_pic_link", "action", "email")