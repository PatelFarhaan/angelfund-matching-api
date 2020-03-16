import datetime
from flask_login import UserMixin
from project import db, login_manager


@login_manager.user_loader
def user_load(user_id):
    return Users.objects.get(pk=user_id)


class Users(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    first_name = db.StringField(max_length=50)
    last_name = db.StringField(max_length=50)
    created = db.DateTimeField(default=datetime.datetime.utcnow())
    email_confirmed = db.BooleanField(default=False)

    meta = {
        'indexes': ['username', 'email', '-created']
        }