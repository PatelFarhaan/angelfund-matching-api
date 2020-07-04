#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
from flask_cors import CORS
from datetime import timedelta
from flask import Flask, session
from flask_login import LoginManager
from common_utilities import CONSTANT
from flask_marshmallow import Marshmallow
from flask_mongoengine import MongoEngine
from itsdangerous import URLSafeTimedSerializer
from common_utilities.flask_jwt_extended import JWTManager


#<==================================================================================================>
#                                         CONFIG
#<==================================================================================================>
app = Flask(__name__)
app.config['SECRET_KEY'] = CONSTANT.SECRET_KEY.value
serial = URLSafeTimedSerializer(CONSTANT.SECRET_KEY.value)
app.config['JWT_SECRET_KEY'] = CONSTANT.JWT_SECRET_KEY.value
app.config['MONGODB_SETTINGS'] = {'host': CONSTANT.TEST_DB_CLUSTER.value}

CORS(app)
db = MongoEngine(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)

login_manager = LoginManager(app)
login_manager.blueprint_login_views = {
    "startup": "startup.login",
    "investor": "investor.login"
}

#<==================================================================================================>
#                                         BLUEPRINT
#<==================================================================================================>
from project.startup.views import startup_blueprint
from project.investor.views import investor_blueprint
from project.error.error_handler import errorpage_blueprint

app.register_blueprint(startup_blueprint)
app.register_blueprint(investor_blueprint)
app.register_blueprint(errorpage_blueprint)