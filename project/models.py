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
    syndicate = db.ListField()
    location = db.StringField()
    password = db.StringField()
    accreditation = db.StringField()
    profile_pic_link = db.StringField()
    approved = db.BooleanField(default=False)
    password_reset_meta_data = db.DictField()
    last_name = db.StringField(max_length=70)
    first_name = db.StringField(max_length=70)
    is_logged_in = db.BooleanField(defalut=False)
    email_confirmed = db.BooleanField(default=False)
    is_google_signup = db.BooleanField(default=False)
    email = db.EmailField(required=True, unique=True)
    created = db.DateTimeField(default=datetime.datetime.utcnow())
    
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
    bio = db.StringField()
    password = db.StringField()
    profile_pic_link = db.StringField()
    approved = db.BooleanField(default=False)
    password_reset_meta_data = db.DictField()
    last_name = db.StringField(max_length=70)
    first_name = db.StringField(max_length=70)
    is_logged_in = db.BooleanField(defalut=False)
    email_confirmed = db.BooleanField(default=False)
    is_google_signup = db.BooleanField(default=False)
    email = db.EmailField(required=True, unique=True)
    created = db.DateTimeField(default=datetime.datetime.utcnow())

    location = db.StringField()
    sectors = db.ListField()
    company_name = db.StringField()
    company_link = db.StringField()
    startup_pitch = db.StringField()
    round_size = db.IntField(default=None)
    raised = db.IntField(default=None)
    progress = db.ListField()
    position = db.StringField()
    num_team_members = db.IntField()
    slide_deck = db.StringField()
    
    # This field is for frontend to decide whether to show a tutorial or not
    first_dashboard_visit = db.BooleanField(default=True)

    meta = dict(indexes=['email', '-created', 'is_google_signup'])

    def get_id(self):
        return {
            "user_id": str(self.id),
            "role": "startup"
        }

    def is_jwt_authenticated(self):
        return self.is_user_authenticated


class SignUpMappings(db.Document):
    deals_data = db.DictField()
    sector_data = db.DictField()
    accreditation_data = db.DictField()