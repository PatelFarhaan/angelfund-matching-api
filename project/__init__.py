from flask import Flask
from flask_login import LoginManager
from common_utilities import CONSTANT
from flask_mongoengine import MongoEngine
from itsdangerous import URLSafeTimedSerializer


############# DETAILS ###################
app = Flask(__name__)
app.config['SECRET_KEY'] = CONSTANT.SECRET_KEY.value
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mongodb://localhost/users'
app.config['MONGODB_SETTINGS'] = {'host': CONSTANT.PRIMARY_DB_CLUSTER.value}
serial = URLSafeTimedSerializer(CONSTANT.SECRET_KEY.value)
db = MongoEngine(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

##############  BLUEPRINT #################

from project.core.views import core_blueprint
from project.users.views import users_blueprint
from project.error.error_handler import errorpage_blueprint

app.register_blueprint(core_blueprint)
app.register_blueprint(users_blueprint)
app.register_blueprint(errorpage_blueprint)