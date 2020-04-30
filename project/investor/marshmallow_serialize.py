from project import ma


class InvestorUserSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "email", "sectors", "deals", "profile_pic_link",
                  "bio", "location", "accreditation", "syndicate", "angel", "prior_investment",
                  "email_confirmed", "approved", "first_dashboard_visit")



class InvestorMLSchema(ma.Schema):
    class Meta:
        fields = ("bio", "sectors", "raised", "progress", "position", "location", "referred_to",
                  "slide_deck", "referred_by", "round_size", "company_link", "company_name",
                  "num_team_members", "startup_pitch", "profile_pic_link", "raised_capital_desc",
                  "password_reset_meta_data", "approved", "last_name", "first_name", "is_logged_in",
                  "email_confirmed", "is_google_signup", "email", "first_dashboard_visit", "created",
                  "show_limit", "matched_week", "deals", "accreditation", "syndicate", "prior_investment",
                  "investor", "feedback", "connected", "passed", "pending", "co_founders", "show_slide_deck",
                  "delete_account", "show_profile", "monday_notification", "count_invited", "count_passed")