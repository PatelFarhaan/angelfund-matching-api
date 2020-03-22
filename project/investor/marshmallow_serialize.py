from project import ma


class InvestorSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "email")





'''
// For serialization purpose, the frontend will need the following fields:
    last_name = db.StringField(max_length=70)
    first_name = db.StringField(max_length=70)
    sectors = db.StringField()
    deals = db.StringField()
    bio = db.StringField()
    location = db.StringField()
    accreditation = db.StringField()
    syndicate = db.StringField()
    angel = db.BooleanField()
'''