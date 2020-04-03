from project import ma


class StartupUserSchema(ma.Schema):
    class Meta:
        fields = ("first_name", "last_name", "email")