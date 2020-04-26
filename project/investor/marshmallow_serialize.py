from project import ma


class InvestorUserSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "email", "sectors", "deals",
                  "bio", "location", "accreditation", "syndicate", "angel",
                  "email_confirmed", "approved", "first_dashboard_visit")


class InvestorMLSchema(ma.Schema):
    class Meta:
        fields = ("email", "sectors", "deals", "investor", "show_profile", "show_limit",
                  "matched_week", "count_invited", "count_passed", "bio", "accreditation",
                  "syndicate", "show_limit")