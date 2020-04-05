import json
import logging
import requests
import threading
from project.models import Startup
from common_utilities import CONSTANT
from project import serial, google_client
from flask_login import login_user, current_user
from flask import url_for, request, Blueprint, jsonify
from common_utilities.file_upload_to_s3 import file_upload_to_s3
from common_utilities.password_reset import password_reset_email
from common_utilities.email_confirmation import email_confirmation
from common_utilities.google_email import google_email_confirmation
from project.startup.marshmallow_serialize import StartupUserSchema
from werkzeug.security import generate_password_hash, check_password_hash
from common_utilities.flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from common_utilities.json_schema_startup_validation import (validate_str_first_page_schema, validate_email_schema,
                                                              validate_str_login_schema, validate_str_password_reset_schema)


logger = logging.getLogger(__name__)
startup_blueprint = Blueprint('startup', __name__, url_prefix='/startup')


@startup_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_request = request.get_json()
        response = validate_str_login_schema(input_request)
        if response["result"]:
            email = response["data"]["email"]
            password = response["data"]["password"]

            user = Startup.objects.filter(email=email).first()
            if user is None:
                message = "user does not exist"
                logger.debug(f"startup does not exixt: {email}")
                return return_data_results(False, message)

            if user.is_google_signup:
                return_obj = {
                    "status_code": 200,
                    "message": "registered with google account",
                    "redirect_url": "https://127.0.0.1:5000/startup/login/callback"
                }
                return jsonify(return_obj)

            if not user.email_confirmed:
                message = "please confirm your email address"
                token = serial.dumps(email, salt='email_confirm')
                link = url_for('startup.email_confirmed', token=token, _external=True)
                thread = threading.Thread(target=email_confirmation, args=(email, link,))
                thread.start()
                return return_data_results(False, message)

            if user and check_password_hash(user.password, password):
                login_user(user)
                user.is_logged_in = True
                user.save()
                logger.debug(f"startup logged in: {email}")

                ma_schema = StartupUserSchema()
                user_objs = ma_schema.dump(user)
                jwt_obj = {"email": email, "model": "Startup"}
                access_token = create_access_token(identity=jwt_obj)
                ret_obj = {
                    "result": True,
                    "user": user_objs,
                    "token": access_token
                }
                return ret_obj
            else:
                logger.debug(f"startup wrong credentials: {email}")
                message = "wrong credentails"
                return return_data_results(False, message)
        else:
            return jsonify(response)

    elif request.method == "GET":
        message = "frontend user login template"
        return return_data_results(True, message)


@startup_blueprint.route('/reset-link/<token>', methods=['GET', 'POST'])
def reset_link(token):  # Both click and time based
    try:
        email = serial.loads(token, salt='email_reset', max_age=int(CONSTANT.PASSWORD_RESET_LINK_AGE.value))
        user = Startup.objects.filter(email=email).first()
        if user:
            if request.method == 'POST':
                input_request = request.get_json()
                response = validate_str_password_reset_schema(input_request)
                if response["result"]:
                    password = response["data"]["password"]
                    if not user.password_reset_meta_data["is_clicked"]:
                        user.password = generate_password_hash(password)
                        user.password_reset_meta_data = {}
                        user.save()
                        logger.debug(f"startup password changed: {email}")
                        message = "password changed successfully"
                        return return_data_results(True, message)
                    else:
                        logger.debug(f"startup password reset link expired: {email}")
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


@startup_blueprint.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        input_request = request.get_json()
        response = validate_email_schema(input_request)
        if response["result"]:
            email = response["data"]["email"]
            user = Startup.objects.filter(email=email).first()

            if user is None:
                logger.debug(f"startup does not exist: {email}")
                message = "user does not exist"
                return return_data_results(False, message)

            token = serial.dumps(user.email, salt='email_reset')
            link = url_for('startup.reset_link', token=token, _external=True)
            user.password_reset_meta_data = {"is_clicked": False}
            user.save()

            thread = threading.Thread(target=password_reset_email, args=(email, link,))
            thread.start()
            logger.debug(f"startup password reset link sent: {email}")
            message = "frontend password reset link sent template"
            return return_data_results(True, message)
        else:
            return jsonify(response)

    elif request.method == "GET":
        message = "frontend forgot password template"
        return return_data_results(True, message)


@startup_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        profile_photo = request.files.get('profile_pic', None)  # This is a form object and not a json

        input_request = request.get_json()
        response = validate_str_first_page_schema(input_request)
        if response["result"]:
            email = response["data"]["email"]

            email_exist = Startup.objects.filter(email=email).first()

            if email_exist:
                logger.debug(f"startup exists: {email}")
                message = "email exists"
                return return_data_results(False, message)

            if profile_photo:
                profile_photo_name = profile_photo.filename.strip().replace(' ', '')
                public_profile_pic_link = file_upload_to_s3(profile_photo, profile_photo_name)

                input_request["profile_pic_link"] = public_profile_pic_link
                input_request["password"] = generate_password_hash(input_request["password"])

                new_user = Startup(**input_request)
                new_user.save()
                logger.debug(f"startup created {email}")
            else:
                input_request["password"] = generate_password_hash(input_request["password"])
                new_user = Startup(**input_request)
                new_user.save()
                logger.debug(f"startup created {email}")

            token = serial.dumps(email, salt='email_confirm')
            link = url_for('startup.email_confirmed', token=token, _external=True)
            thread = threading.Thread(target=email_confirmation, args=(email, link,))
            thread.start()
            message = "frontend email confirmation template"
            return return_data_results(True, message)
        else:
            return jsonify(response)

    elif request.method == "GET":
        message = "frontend register template"
        return return_data_results(True, message)


@startup_blueprint.route('/email-confirmed/<token>', methods=['GET', 'POST'])
def email_confirmed(token):
    email = serial.loads(token, salt='email_confirm')
    user = Startup.objects.filter(email=email).first()

    if user:
        user.email_confirmed = True
        user.save()
        logger.debug(f"startup email confirmed {email}")
        message = "frontend email confirmed template"
        return return_data_results(True, message)
    else:
        logger.debug(f"startup does not exist {email}")
        message = "user does not exist"
        return return_data_results(False, message)


@startup_blueprint.route('/logout', methods=["POST"])
@jwt_required
def logout():
    current_user_email = get_jwt_identity()["email"]
    user_model = get_jwt_identity()["model"]
    if user_model != "Startup":
        return jsonify({
            "return": False,
            "message": "invalid token"
        })
    user_obj = Startup.objects.filter(email=current_user_email).first()
    user_obj.is_logged_in = False
    user_obj.save()
    return jsonify({
        "result": True,
        "status_code": 200,
        "message": "user logged off"
    })

@startup_blueprint.route('/update-info', methods=['PATCH'])
@jwt_required
def update_info():
    user_email = get_jwt_identity()["email"]
    user_obj = Startup.objects.filter(email=user_email).first()
    if user_obj.is_logged_in:
        input_data = request.get_json()    # code will give 500 error if no json if passed
        available_fields = {"location", "sectors", "company_name", "company_link", 
                            "startup_pitch", "bio", "round_size", "raised", 
                            "progress", "position", "num_team_members", "slide_deck"}
        for field in input_data:
            if field in available_fields:
                setattr(user_obj, field, input_data[field])
            else:
                message = "invalid user field"
                return return_data_results(False, message)
        user_obj.save()
        ma_schema = StartupUserSchema()
        user_objs = ma_schema.dump(user_obj)
        ret_obj = {
            "result": True,
            "user": user_objs,
        }
        return ret_obj
    else:
        message = "user is not authenticated"
        return return_data_results(False, message)

@startup_blueprint.route('/test', methods=["GET"])
@jwt_required
def test():
    current_user_email = get_jwt_identity()["email"]
    user_model = get_jwt_identity()["model"]
    if user_model != "Startup":
        return jsonify({
            "return": False,
            "message": "invalid token"
        })
    user_obj = Startup.objects.get(email=current_user_email)
    if not user_obj.is_logged_in:
        return jsonify({
            "return": False,
            "message": "user logged out"
        })

    return jsonify({
        "result": True,
        "status_code": 200,
        "message": "logged in view"
    })



##############################################################################
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