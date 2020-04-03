import datetime
from flask_login import UserMixin
from project import db, login_manager


@login_manager.user_loader
def user_load(user_obj):
    user_id = user_obj["user_id"]
    if user_obj["role"] == "investor":
        return Investor.objects.get(pk=user_id)
    elif user_obj["role"] == "startup":
        return Startup.objects.get(pk=user_id)


class Investor(db.Document, UserMixin):
    bio = db.StringField()
    deals = db.StringField()
    sectors = db.ListField()
    angel = db.BooleanField()
    location = db.StringField()
    syndicate = db.StringField()
    password = db.StringField()
    accreditation = db.StringField()
    profile_pic_link = db.StringField()
    password_reset_meta_data = db.DictField()
    last_name = db.StringField(max_length=70)
    first_name = db.StringField(max_length=70)
    is_logged_in = db.BooleanField(defalut=False)
    email_confirmed = db.BooleanField(default=False)
    is_google_signup = db.BooleanField(default=False)
    email = db.EmailField(required=True, unique=True)
    created = db.DateTimeField(default=datetime.datetime.utcnow())
    
    deals = db.StringField()
    bio = db.StringField()
    location = db.StringField()
    accreditation = db.StringField()
    syndicate = db.ListField()
    angel = db.BooleanField()
    approved = db.BooleanField(default=False)
    
    # This field is for frontend to decide whether to show a tutorial or not
    first_dashboard_visit = db.BooleanField(default=True)

    meta = dict(indexes=['email', '-created', 'is_google_signup'])

    def get_id(self):
        return {
            "user_id": str(self.id),
            "role": "investor"
        }

    def is_jwt_authenticated(self):
        return self.is_user_authenticated


class Startup(db.Document, UserMixin):
    password = db.StringField()
    profile_pic_link = db.StringField()
    password_reset_meta_data = db.DictField()
    last_name = db.StringField(max_length=70)
    first_name = db.StringField(max_length=70)
    email_confirmed = db.BooleanField(default=False)
    is_google_signup = db.BooleanField(default=False)
    email = db.EmailField(required=True, unique=True)
    created = db.DateTimeField(default=datetime.datetime.utcnow())

    meta = dict(indexes=['email', '-created'])

    def get_id(self):
        return {
            "user_id": str(self.id),
            "role": "startup"
        }


class SignUpMappings(db.Document):
    deals_data = db.DictField()
    sector_data = db.DictField()
    accreditation_data = db.DictField()