import datetime
from flask_login import UserMixin
from project import db, login_manager


#<==================================================================================================>
#                                      UPDATE INFORMATION
#<==================================================================================================>
@login_manager.user_loader
def user_load(user_obj):
    user_id = user_obj["user_id"]
    if user_obj["role"] == "investor":
        return Investor.objects.get(pk=user_id)
    elif user_obj["role"] == "startup":
        return Startup.objects.get(pk=user_id)


#<==================================================================================================>
#                                 INVESTOR COLLECTION
#<==================================================================================================>
class Investor(db.Document, UserMixin):
    bio = db.StringField()
    passed = db.DictField()
    pending = db.DictField()
    deals = db.ListField()
    sectors = db.ListField()
    syndicate = db.ListField()
    connected = db.DictField()
    location = db.StringField()
    password = db.StringField()
    accreditation = db.StringField()
    prior_investments = db.ListField()
    profile_pic_link = db.StringField()
    matched_week = db.IntField(default=0)
    count_passed = db.IntField(default=0)
    show_limit = db.IntField(default=100)
    count_invited = db.IntField(default=0)
    all_transaction_fields = db.DictField()
    investor = db.BooleanField(default=True)
    password_reset_meta_data = db.DictField()
    approved = db.BooleanField(default=False)
    last_name = db.StringField(max_length=70)
    first_name = db.StringField(max_length=70)
    show_profile = db.BooleanField(default=True)
    first_invite = db.BooleanField(default=True)
    is_logged_in = db.BooleanField(defalut=False)
    delete_account = db.BooleanField(default=False)
    email_confirmed = db.BooleanField(default=False)
    is_google_signup = db.BooleanField(default=False)
    email = db.EmailField(required=True, unique=True)
    monday_notification = db.BooleanField(default=True)
    first_dashboard_visit = db.BooleanField(default=True)
    invite_accepted_notify = db.BooleanField(default=True)
    created = db.DateTimeField(default=datetime.datetime.utcnow())

    meta = dict(indexes=['email', '-created', 'is_google_signup'], strict=False)

    def get_id(self):
        return {
            "user_id": str(self.id),
            "role": "investor"}

    def is_jwt_authenticated(self):
        return self.is_user_authenticated


#<==================================================================================================>
#                                  STARTUP COLLECTION
#<==================================================================================================>
class Startup(db.Document, UserMixin):
    raised = db.IntField()
    bio = db.StringField()
    passed = db.DictField()
    pending = db.DictField()
    sectors = db.ListField()
    progress = db.ListField()
    feedback = db.DictField()
    connected = db.DictField()
    round_size = db.IntField()
    position = db.StringField()
    password = db.StringField()
    location = db.StringField()
    co_founders = db.ListField()
    count_passed = db.IntField()
    count_invited = db.IntField()
    slide_deck = db.StringField()
    company_link = db.StringField()
    company_name = db.StringField()
    num_team_members = db.IntField()
    startup_pitch = db.StringField()
    profile_pic_link = db.StringField()
    show_limit = db.IntField(default=3)
    matched_week = db.IntField(default=0)
    raised_capital_desc = db.StringField()
    all_transaction_fields = db.DictField()
    investor = db.BooleanField(default=False)
    password_reset_meta_data = db.DictField()
    approved = db.BooleanField(default=False)
    last_name = db.StringField(max_length=70)
    first_name = db.StringField(max_length=70)
    show_profile = db.BooleanField(default=True)
    first_invite = db.BooleanField(default=True)
    is_logged_in = db.BooleanField(defalut=False)
    show_slide_deck = db.BooleanField(default=True)
    delete_account = db.BooleanField(default=False)
    email_confirmed = db.BooleanField(default=False)
    is_google_signup = db.BooleanField(default=False)
    email = db.EmailField(required=True, unique=True)
    monday_notification = db.BooleanField(default=True)
    first_dashboard_visit = db.BooleanField(default=True)
    invite_accepted_notify = db.BooleanField(default=True)
    created = db.DateTimeField(default=datetime.datetime.utcnow())

    meta = dict(indexes=['email', '-created', 'is_google_signup'], strict=False)

    def get_id(self):
        return {
            "user_id": str(self.id),
            "role": "startup"}

    def is_jwt_authenticated(self):
        return self.is_user_authenticated


#<==================================================================================================>
#                                   REFERRALS COLLECTION
#<==================================================================================================>
class Referrals(db.Document):
    email = db.EmailField(required=True, unique=True)
    details = db.DictField()

    meta = dict(indexes=['email'])


#<==================================================================================================>
#                                   NOT USED IN PHASE 1
#<==================================================================================================>
class SignUpMappings(db.Document):
    deals_data = db.DictField()
    sector_data = db.DictField()
    accreditation_data = db.DictField()


class InvestorSubscriptionEmails(db.Document):
    email = db.EmailField()

    meta = dict(indexes=['email'])


class StartupSubscriptionEmails(db.Document):
    email = db.EmailField()

    meta = dict(indexes=['email'])


