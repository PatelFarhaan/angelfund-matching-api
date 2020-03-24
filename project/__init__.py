from flask import Flask
from flask_login import LoginManager
from common_utilities import CONSTANT
from flask_mongoengine import MongoEngine
from flask_marshmallow import Marshmallow
from itsdangerous import URLSafeTimedSerializer
from oauthlib.oauth2 import WebApplicationClient


############# DETAILS ###################
app = Flask(__name__)
app.config['SECRET_KEY'] = CONSTANT.SECRET_KEY.value

from flask_jwt_extended import JWTManager
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity



serial = URLSafeTimedSerializer(CONSTANT.SECRET_KEY.value)
google_client = WebApplicationClient(CONSTANT.GOOGLE_CLIENT_ID.value)
app.config['MONGODB_SETTINGS'] = {'host': CONSTANT.PRIMARY_DB_CLUSTER.value}
db = MongoEngine(app)
ma = Marshmallow(app)
login_manager = LoginManager(app)

login_manager.blueprint_login_views = {
    "startup": "startup.login",
    "investor": "investor.login"
}

##############  BLUEPRINT #################

from project.startup.views import startup_blueprint
from project.investor.views import investor_blueprint
from project.error.error_handler import errorpage_blueprint

app.register_blueprint(startup_blueprint)
app.register_blueprint(investor_blueprint)
app.register_blueprint(errorpage_blueprint)

