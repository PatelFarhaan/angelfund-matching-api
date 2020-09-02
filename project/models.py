#<==================================================================================================>
#                                       IMPORTS
#<==================================================================================================>
import datetime
from flask_login import UserMixin
from project import db, login_manager


#<==================================================================================================>
#                                       UPDATE INFORMATION
#<==================================================================================================>
@login_manager.user_loader
def user_load(user_obj):
    user_id = user_obj["user_id"]
    if user_obj["role"] == "investor":
        return Investor.objects.get(pk=user_id)
    elif user_obj["role"] == "startup":
        return Startup.objects.get(pk=user_id)


#<==================================================================================================>
#                                    INVESTOR COLLECTION
#<==================================================================================================>
class Investor(db.Document, UserMixin):
    deals = db.ListField()
    bio = db.StringField()
    passed = db.DictField()
    pending = db.DictField()
    sectors = db.ListField()
    connected = db.DictField()
    syndicate = db.ListField()
    location = db.StringField()
    password = db.StringField()
    discover_cards = db.ListField()
    accreditation = db.StringField()
    prior_investments = db.ListField()
    show_limit = db.IntField(default=3)
    all_transaction_fields = db.DictField()
    investor = db.BooleanField(default=True)
    password_reset_meta_data = db.DictField()
    approved = db.BooleanField(default=False)
    last_name = db.StringField(max_length=70)
    first_name = db.StringField(max_length=70)
    passowrd_confirm_meta_data = db.DictField()
    first_invite = db.BooleanField(default=True)
    show_profile = db.BooleanField(default=True)
    is_logged_in = db.BooleanField(defalut=False)
    profile_pic_link = db.StringField(default=None)
    delete_account = db.BooleanField(default=False)
    email_confirmed = db.BooleanField(default=False)
    is_google_signup = db.BooleanField(default=False)
    email = db.EmailField(required=True, unique=True)
    monday_notification = db.BooleanField(default=True)
    total_transaction_this_week = db.IntField(default=0)
    prior_inv_completed = db.BooleanField(default=False)
    first_dashboard_visit = db.BooleanField(default=True)
    invite_accepted_notify = db.BooleanField(default=True)
    created = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['email', '-created', 'is_google_signup', 'is_logged_in'])

    def get_id(self):
        return {
            "user_id": str(self.id),
            "role": "investor"}


#<==================================================================================================>
#                                     STARTUP COLLECTION
#<==================================================================================================>
class Startup(db.Document, UserMixin):
    raised = db.IntField()
    bio = db.StringField()
    deals = db.ListField()
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
    slide_deck = db.StringField()
    discover_cards = db.ListField()
    company_name = db.StringField()
    num_team_members = db.IntField()
    startup_pitch = db.StringField()
    show_limit = db.IntField(default=3)
    all_transaction_fields = db.DictField()
    investor = db.BooleanField(default=False)
    password_reset_meta_data = db.DictField()
    approved = db.BooleanField(default=False)
    last_name = db.StringField(max_length=70)
    first_name = db.StringField(max_length=70)
    company_link = db.StringField(default=None)
    passowrd_confirm_meta_data = db.DictField()
    first_invite = db.BooleanField(default=True)
    show_profile = db.BooleanField(default=True)
    is_logged_in = db.BooleanField(defalut=False)
    profile_pic_link = db.StringField(default=None)
    show_slide_deck = db.BooleanField(default=True)
    delete_account = db.BooleanField(default=False)
    email_confirmed = db.BooleanField(default=False)
    is_google_signup = db.BooleanField(default=False)
    email = db.EmailField(required=True, unique=True)
    co_founders_check = db.BooleanField(default=False)
    company_logo_check = db.BooleanField(default=False)
    monday_notification = db.BooleanField(default=True)
    total_transaction_this_week = db.IntField(default=0)
    first_dashboard_visit = db.BooleanField(default=True)
    invite_accepted_notify = db.BooleanField(default=True)
    created = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['email', '-created', 'is_google_signup', 'is_logged_in'])

    def get_id(self):
        return {
            "user_id": str(self.id),
            "role": "startup"}


#<==================================================================================================>
#                                     REFERRALS COLLECTION
#<==================================================================================================>
class Referrals(db.Document):
    email = db.EmailField(required=True, unique=True)
    details = db.DictField()

    meta = dict(indexes=['email'])


#<==================================================================================================>
#                                       NEW USERS DAILY
#<==================================================================================================>
class InvDailyNewUsers(db.Document):
    count = db.IntField(default=0)
    current = db.BooleanField(default=False)
    current_dt = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['count', 'current_dt'])


class StrDailyNewUsers(db.Document):
    count = db.IntField(default=0)
    current = db.BooleanField(default=False)
    current_dt = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['count', 'current_dt'])


#<==================================================================================================>
#                                       NEW USERS WEEKLY
#<==================================================================================================>
class InvWeeklyNewUsers(db.Document):
    count = db.IntField(default=0)
    current = db.BooleanField(default=False)
    current_dt = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['count', 'current_dt'])


class StrWeeklyNewUsers(db.Document):
    count = db.IntField(default=0)
    current = db.BooleanField(default=False)
    current_dt = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['count', 'current_dt'])


#<==================================================================================================>
#                                       NEW USERS MONTHLY
#<==================================================================================================>
class InvMonthlyNewUsers(db.Document):
    count = db.IntField(default=0)
    current = db.BooleanField(default=False)
    current_dt = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['count', 'current_dt'])


class StrMonthlyNewUsers(db.Document):
    count = db.IntField(default=0)
    current = db.BooleanField(default=False)
    current_dt = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['count', 'current_dt'])


#<==================================================================================================>
#                                      DAILY UNIQUE USERS
#<==================================================================================================>
class InvUniqueUsersDaily(db.Document):
    users_dict = db.DictField()
    count = db.IntField(default=0)
    current = db.BooleanField(default=False)
    current_dt = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['count', 'current_dt', 'users_dict', 'current'])


class StrUniqueUsersDaily(db.Document):
    users_dict = db.DictField()
    count = db.IntField(default=0)
    current = db.BooleanField(default=False)
    current_dt = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['count', 'current_dt', 'users_dict', 'current'])


#<==================================================================================================>
#                                      WEEKLY UNIQUE USERS
#<==================================================================================================>
class InvUniqueUsersWeekly(db.Document):
    users_dict = db.DictField()
    count = db.IntField(default=0)
    current = db.BooleanField(default=False)
    current_dt = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['count', 'current_dt', 'users_dict', 'current'])


class StrUniqueUsersWeekly(db.Document):
    users_dict = db.DictField()
    count = db.IntField(default=0)
    current = db.BooleanField(default=False)
    current_dt = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['count', 'current_dt', 'users_dict', 'current'])


#<==================================================================================================>
#                                      MONTHLY UNIQUE USERS
#<==================================================================================================>
class InvUniqueUsersMonthly(db.Document):
    users_dict = db.DictField()
    count = db.IntField(default=0)
    current = db.BooleanField(default=False)
    current_dt = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['count', 'current_dt', 'users_dict', 'current'])


class StrUniqueUsersMonthly(db.Document):
    users_dict = db.DictField()
    count = db.IntField(default=0)
    current = db.BooleanField(default=False)
    current_dt = db.DateTimeField(default=datetime.datetime.now)

    meta = dict(indexes=['count', 'current_dt', 'users_dict', 'current'])


#<==================================================================================================>
#                                    INVESTOR RETENTION RATE
#<==================================================================================================>
class InvRetention(db.Document):
    daily = db.ListField()
    weekly = db.ListField()
    monthly = db.ListField()

    meta = dict(indexes=['daily', 'weekly', 'monthly'])


#<==================================================================================================>
#                                    STARTUP RETENTION RATE
#<==================================================================================================>
class StrRetention(db.Document):
    daily = db.ListField()
    weekly = db.ListField()
    monthly = db.ListField()

    meta = dict(indexes=['daily', 'weekly', 'monthly'])


#<==================================================================================================>
#                                   INVESTOR ANALYTICS
#<==================================================================================================>
class InvestorUserAnalytics(db.Document):
    daily = db.ListField()
    weekly = db.ListField()
    monthly = db.ListField()
    last_login = db.DateTimeField()
    email = db.EmailField(required=True, unique=True)

    meta = dict(indexes=['email'])


#<==================================================================================================>
#                                    STARTUP ANALYTICS
#<==================================================================================================>
class StartupUserAnalytics(db.Document):
    daily = db.ListField()
    weekly = db.ListField()
    monthly = db.ListField()
    last_login = db.DateTimeField()
    email = db.EmailField(required=True, unique=True)

    meta = dict(indexes=['email'])