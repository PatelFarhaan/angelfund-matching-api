import datetime
from flask_login import UserMixin
from project import db, login_manager


@login_manager.user_loader
def user_load(user_id):
    return Users.objects.get(pk=user_id)


class Users(db.Document, UserMixin):
    password = db.StringField(required=True)
    password_reset_meta_data = db.DictField()
    last_name = db.StringField(max_length=50)
    first_name = db.StringField(max_length=50)
    email_confirmed = db.BooleanField(default=False)
    email = db.EmailField(required=True, unique=True)
    username = db.StringField(required=True, unique=True)
    created = db.DateTimeField(default=datetime.datetime.utcnow())

    meta = {
        'indexes': ['username', 'email', '-created']
        }