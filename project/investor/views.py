import json
import logging
import requests
import threading
from flask_login import login_user
from project.models import Investor
from common_utilities import CONSTANT
from project import serial, google_client
from flask import url_for, request, Blueprint, jsonify, redirect
from common_utilities.file_upload_to_s3 import file_upload_to_s3
from common_utilities.password_reset import password_reset_email
from common_utilities.email_confirmation import email_confirmation
from common_utilities.google_email import google_email_confirmation
from project.investor.marshmallow_serialize import InvestorUserSchema
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from common_utilities.json_schema_investor_validation import (validate_inv_first_page_schema,
                                                              validate_inv_login_schema, validate_email_schema,
                                                              validate_inv_password_reset_schema)


logger = logging.getLogger(__name__)
investor_blueprint = Blueprint('investor', __name__, url_prefix='/investor')


@investor_blueprint.route("/google-login")
def google_login():
    google_provider_cfg = requests.get(CONSTANT.GOOGLE_DISCOVERY_URL.value).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = google_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="https://127.0.0.1:5000/investor/login/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@investor_blueprint.route("/login/callback")
def callback():
    code = request.args.get("code")
    google_provider_cfg = requests.get(CONSTANT.GOOGLE_DISCOVERY_URL.value).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = google_client.prepare_token_request(
        token_endpoint,
        code=code,
        redirect_url=request.base_url,
        authorization_response=request.url)

    token_response = requests.post(
        token_url,
        data=body,
        headers=headers,
        auth=(CONSTANT.GOOGLE_CLIENT_ID.value, CONSTANT.GOOGLE_CLIENT_SECRET.value))

    google_client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = google_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        email = userinfo_response.json().get("email", None)

        user = Investor.objects.filter(email=email).first()
        if user:
            login_user(user)
            logger.debug(f"investor logged in: {email}")

            ma_schema = InvestorUserSchema()
            user_objs = ma_schema.dump(user)
            access_token = create_access_token(identity=email)
            user.is_authenticated = True
            ret_obj = {
                "result": True,
                "user": user_objs,
                "token": access_token,
            }
            return ret_obj
        else:
            picture = userinfo_response.json().get("picture", None)
            first_name = userinfo_response.json().get("given_name", None)
            last_name = userinfo_response.json().get("family_name", None)

            # noinspection PyArgumentList
            new_user = Investor(email=email,
                                last_name=last_name,
                                email_confirmed=True,
                                first_name=first_name,
                                is_google_signup=True,
                                profile_pic_link=picture)
            new_user.save()
            logger.debug(f"investor created {email} via Google OAuth")

            thread = threading.Thread(target=google_email_confirmation, args=(email,))
            thread.start()

            user = Investor.objects.filter(email=email).first()
            login_user(user)

            logger.debug(f"investor logged in: {email}")

            ma_schema = InvestorUserSchema()
            user_objs = ma_schema.dump(user)
            access_token = create_access_token(identity=email)
            ret_obj = {
                "result": True,
                "user": user_objs,
                "token": access_token,
            }
            return ret_obj
    else:
        message = "User email not available or not verified by Google."
        logger.debug(f"{message}: {userinfo_response.json().get('email', 'email_not_mentioned')}")
        return return_data_results(False, message, 400)


@investor_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_request = request.get_json()
        response = validate_inv_login_schema(input_request)
        if response["result"]:
            email = response["data"]["email"]
            password = response["data"]["password"]

            user = Investor.objects.filter(email=email).first()
            if user is None:
                message = "user does not exist"
                logger.debug(f"investor does not exixt: {email}")
                return return_data_results(False, message)

            if user.is_google_signup:
                return_obj = {
                    "status_code": 200,
                    "message": "registered with google account",
                    "redirect_url": "https://127.0.0.1:5000/investor/login/callback"
                }
                return jsonify(return_obj)

            if not user.email_confirmed:
                message = "please confirm your email address"
                token = serial.dumps(email, salt='email_confirm')
                link = url_for('investor.email_confirmed', token=token, _external=True)
                thread = threading.Thread(target=email_confirmation, args=(email, link,))
                thread.start()
                return return_data_results(False, message)

            if user and check_password_hash(user.password, password):
                login_user(user)
                logger.debug(f"investor logged in: {email}")

                ma_schema = InvestorUserSchema()
                user_objs = ma_schema.dump(user)
                access_token = create_access_token(identity=email)
                ret_obj = {
                    "result": True,
                    "user": user_objs,
                    "token": access_token,
                }
                return ret_obj
            else:
                logger.debug(f"investor wrong credentials: {email}")
                message = "wrong credentails"
                return return_data_results(False, message)
        else:
            return jsonify(response)

    elif request.method == "GET":
        message = "frontend user login template"
        return return_data_results(True, message)


@investor_blueprint.route('/reset-link/<token>', methods=['GET','POST'])
def reset_link(token):  # Both click and time based
    try:
        email = serial.loads(token, salt='email_reset', max_age=int(CONSTANT.PASSWORD_RESET_LINK_AGE.value))
        user = Investor.objects.filter(email=email).first()
        if user:
            if request.method == 'POST':
                input_request = request.get_json()
                response = validate_inv_password_reset_schema(input_request)
                if response["result"]:
                    password = response["data"]["password"]
                    if not user.password_reset_meta_data["is_clicked"]:
                        user.password = generate_password_hash(password)
                        user.password_reset_meta_data = {}
                        user.save()
                        logger.debug(f"investor password changed: {email}")
                        message = "password changed successfully"
                        return return_data_results(True, message)
                    else:
                        logger.debug(f"investor password reset link expired: {email}")
                        message = "password reset link expired"
                        return return_data_results(False, message)
                else:
                    return jsonify(response)

            elif request.method == "GET":
                message = "frontend password reset template"
                return return_data_results(True, message)
    except:
        message = "password reset link expired"
        return return_data_results(False, message)


@investor_blueprint.route('/forgot-password', methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        input_request = request.get_json()
        response = validate_email_schema(input_request)
        if response["result"]:
            email = response["data"]["email"]
            user = Investor.objects.filter(email=email).first()

            if user is None:
                logger.debug(f"investor does not exist: {email}")
                message = "user does not exist"
                return return_data_results(False, message)

            token = serial.dumps(user.email, salt='email_reset')
            link = url_for('investor.reset_link', token=token, _external=True)
            user.password_reset_meta_data = {"is_clicked": False}
            user.save()

            thread = threading.Thread(target=password_reset_email, args=(email, link,))
            thread.start()
            logger.debug(f"investor password reset link sent: {email}")
            message = "frontend password reset link sent template"
            return return_data_results(True, message)
        else:
            return jsonify(response)

    elif request.method == "GET":
        message = "frontend forgot password template"
        return return_data_results(True, message)


@investor_blueprint.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        profile_photo = request.files.get('profile_pic', None)     # This is a form object and not a json

        input_request = request.get_json()
        response = validate_inv_first_page_schema(input_request)
        if response["result"]:
            email = response["data"]["email"]

            email_exist = Investor.objects.filter(email=email).first()

            if email_exist:
                logger.debug(f"investor exists: {email}")
                message = "email exists"
                return return_data_results(False, message)

            if profile_photo:
                profile_photo_name = profile_photo.filename.strip().replace(' ', '')
                public_profile_pic_link = file_upload_to_s3(profile_photo, profile_photo_name)

                input_request["profile_pic_link"] = public_profile_pic_link
                input_request["password"] = generate_password_hash(input_request["password"])

                new_user = Investor(**input_request)
                new_user.save()
                logger.debug(f"investor created {email}")
            else:
                input_request["password"] = generate_password_hash(input_request["password"])
                new_user = Investor(**input_request)
                new_user.save()
                logger.debug(f"investor created {email}")

            token = serial.dumps(email, salt='email_confirm')
            link = url_for('investor.email_confirmed', token=token, _external=True)
            thread = threading.Thread(target=email_confirmation, args=(email, link,))
            thread.start()
            message = "frontend email confirmation template"
            return return_data_results(True, message)
        else:
            return jsonify(response)
    
    elif request.method == "GET":
        message = "frontend register template"
        return return_data_results(True, message)


@investor_blueprint.route('/email-confirmed/<token>', methods=['GET','POST'])
def email_confirmed(token):
    email = serial.loads(token, salt='email_confirm')
    user = Investor.objects.filter(email=email).first()
    if user:
        user.email_confirmed = True
        user.save()
        logger.debug(f"investor email confirmed {email}")
        message = "frontend email confirmed template"
        return return_data_results(True, message)
    else:
        logger.debug(f"investor does not exist {email}")
        message = "user does not exist"
        return return_data_results(False, message)


@investor_blueprint.route('/test', methods=["GET"])
@jwt_required
def test():
    current_user_email = get_jwt_identity()
    print(current_user_email, type(current_user_email))
    return jsonify({
        "result": "logged in view",
        "status_code": 200
    })


##################################################   *** HELPERS ***   ####################################################
def return_none_results(name, status_code=200):
    return_obj = {
        "result": False,
        "status_code": status_code,
        "message": f"{name} cannot be empty"
    }
    return jsonify(return_obj)


def return_data_results(result, message, status_code=200):
    return_obj = {
        "result": result,
        "status_code": status_code,
        "message": message
    }
    return jsonify(return_obj)