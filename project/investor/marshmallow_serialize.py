from project import ma


class InvestorUserSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "email", "sectors", "deals",
                  "bio", "location", "accreditation", "syndicate", "angel", 
                  "email_confirmed", "account_approved")
