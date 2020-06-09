#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
from flask_cors import CORS
from datetime import timedelta
from common_utilities import CONSTANT
from flask_mongoengine import MongoEngine
from flask_marshmallow import Marshmallow
from itsdangerous import URLSafeTimedSerializer
from flask import Flask, session
from flask_login import LoginManager
from common_utilities.flask_jwt_extended import JWTManager

#<==================================================================================================>
#                                         CONFIG
#<==================================================================================================>
app = Flask(__name__)
app.config['SECRET_KEY'] = CONSTANT.SECRET_KEY.value
app.config['JWT_SECRET_KEY'] = CONSTANT.JWT_SECRET_KEY.value

serial = URLSafeTimedSerializer(CONSTANT.SECRET_KEY.value)
app.config['MONGODB_SETTINGS'] = {'host': CONSTANT.PRIMARY_DB_CLUSTER.value}
db = MongoEngine(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

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