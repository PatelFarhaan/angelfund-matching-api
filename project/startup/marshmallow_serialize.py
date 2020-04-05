from project import ma


class StartupUserSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "email", "password", "location", 
                    "sectors", "company_name", "company_link", "startup_pitch", 
                    "bio", "round_size", "raised", "progress", "position",
                    "num_team_members", "slide_deck", "approved", "email_confirmed",
                    "first_dashboard_visit")