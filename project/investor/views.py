import logging
import threading
from project import serial
from project.models import Investor
from common_utilities import CONSTANT
from flask import url_for, request, Blueprint, jsonify
from common_utilities.file_upload_to_s3 import file_upload_to_s3
from common_utilities.password_reset import password_reset_email
from project.investor.marshmallow_serialize import InvestorSchema
from common_utilities.email_confirmation import email_confirmation
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from common_utilities.json_schema_investor_validation import (validate_inv_first_page_schema,
                                                              validate_inv_login_schema, validate_email_schema,
                                                              validate_inv_password_reset_schema)


logger = logging.getLogger(__name__)
investor_blueprint = Blueprint('investor', __name__, url_prefix='/investor')


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

                ma_schema = InvestorSchema()
                return ma_schema.dump(user)
                # generate jwt token
                # message = "user logged in successfully"
                # return return_data_results(True, message)
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


@investor_blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    email = current_user.email
    logout_user()
    logger.debug(f"investor logged out: {email}")
    message = "user logged out successfully"
    return return_data_results(True, message)


@investor_blueprint.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        profile_photo = request.files.get('profile_pic', None)     # This is a form object and not a json

        input_request = request.get_json()
        response = validate_inv_first_page_schema(input_request)
        if response["result"]:
            email = response["data"]["email"]
            password = response["data"]["password"]
            last_name = response["data"]["last_name"]
            first_name = response["data"]["first_name"]
            email_exist = Investor.objects.filter(email=email).first()

            if email_exist:
                logger.debug(f"investor exists: {email}")
                message = "email exists"
                return return_data_results(False, message)

            if profile_photo:
                profile_photo_name = profile_photo.filename.strip().replace(' ', '')
                public_profile_pic_link = file_upload_to_s3(profile_photo, profile_photo_name)
                # noinspection PyArgumentList
                new_user = Investor(email=email,
                                    last_name=last_name,
                                    first_name=first_name,
                                    profile_pic_link=public_profile_pic_link,
                                    password=generate_password_hash(password))
                new_user.save()
                logger.debug(f"investor created {email}")
            else:
                # noinspection PyArgumentList
                new_user = Investor(email=email,
                                    last_name=last_name,
                                    first_name=first_name,
                                    password=generate_password_hash(password))
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


@investor_blueprint.route('/update-info', methods=['PATCH'])
@login_required
def update_info():
    if current_user.is_authenticated:
        input_data = request.get_json()
        input_data_fields = [*input_data]
        available_fields = {"sectors", "deals", "bio", "location",
                            "accreditation", "syndicate", "angel", "investor"}
        # for field in available_fields:
        #     if field in input_data_fields:
        #         setattr(current_user, field, input_data[field])
        for field in input_data_fields:
            if field in available_fields:
                setattr(current_user, field, input_data[field])
            else:
                message = "invalid user field"
                return return_data_results(False, message)
    else:
        message = "user is not authenticated"
        return return_data_results(False, message)


@investor_blueprint.route('/test', methods=["GET"])
@login_required
def test():
    return jsonify({
        "result": "logged in view",
        "status_code": 200
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