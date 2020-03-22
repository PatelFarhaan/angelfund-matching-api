from project import ma


class InvestorUserSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "sectors", "deals", "bio", "location", "accreditation", "syndicate", "angel")