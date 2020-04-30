import os
import uuid
import magic     # pip install python-magic-bin==0.4.14
import shutil
import logging
import requests
import threading
from project import serial
from common_utilities.matching_db import insert_into_matching, update_into_matching, get_matching_data, process_all_str_data
from common_utilities.ml_apis import get_discover
from flask_login import login_user
from common_utilities import CONSTANT
from project.models import Investor, ReferralLinks, Startup
from flask import url_for, request, Blueprint, jsonify
from common_utilities.company_images import company_images_api
from common_utilities.password_reset import password_reset_email
from common_utilities.email_confirmation import email_confirmation
from common_utilities.google_email import google_email_confirmation
from project.investor.marshmallow_serialize import InvestorUserSchema, InvestorMLSchema
from common_utilities.get_inv_common_mappings import get_common_mapping
from common_utilities.mime_files_upload import profile_pic_upload_to_s3
from werkzeug.security import generate_password_hash, check_password_hash
from common_utilities.flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from common_utilities.json_schema_investor_validation import (validate_inv_first_page_schema, validate_email_schema, validate_dashboard_schema,
                                                              validate_referrer_schema, validate_company_schema,
                                                              validate_google_schema, validate_inv_login_schema, validate_inv_password_reset_schema)


logger = logging.getLogger(__name__)
investor_blueprint = Blueprint('investor', __name__, url_prefix='/investor')


@investor_blueprint.route("/google-token", methods=["POST"])
def google_token():
    input_request = request.get_json()
    response = validate_google_schema(input_request)

    if response["result"]:
        token = response["data"]["token"]

        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        try:
            userinfo_response = requests.request("GET", url, headers={}, data={})
            if userinfo_response.status_code == 200:
                if userinfo_response.json().get("email_verified"):
                    email = userinfo_response.json().get("email")

                    user = Investor.objects.filter(email=email).first()
                    if user:
                        login_user(user)
                        user.is_logged_in = True
                        user.save()
                        logger.debug(f"investor logged in: {email}")

                        ma_schema = InvestorUserSchema()
                        user_objs = ma_schema.dump(user)
                        jwt_obj = {"email": email, "model": "Investor"}
                        access_token = create_access_token(identity=jwt_obj)

                        ret_obj = {
                            "result": True,
                            "user": user_objs,
                            "token": access_token
                        }
                        return ret_obj
                    else:
                        picture = userinfo_response.json().get("picture", None)
                        first_name = userinfo_response.json().get("given_name", None)
                        last_name = userinfo_response.json().get("family_name", None)

                        user_dict = dict(email = email,
                                         last_name = last_name,
                                         email_confirmed = True,
                                         first_name = first_name,
                                         is_google_signup = True,
                                         profile_pic_link = picture)

                        # noinspection PyArgumentList
                        new_user = Investor(**user)
                        new_user.save()

                        user_dict["investor"] = True
                        ml_schema = InvestorMLSchema()
                        user = Investor.objects.filter(email=email).first()
                        ml_schema_resp = ml_schema.dump(user)
                        if not insert_into_matching(email, ml_schema_resp):
                            pass
                            # todo: shoot out a mail to angelfund team to get the data from investor db and dump it to matching db

                        logger.debug(f"investor created {email} via Google OAuth")

                        thread = threading.Thread(target=google_email_confirmation, args=(email,))
                        thread.start()

                        user = Investor.objects.filter(email=email).first()
                        login_user(user)
                        user.is_logged_in = True
                        user.save()
                        logger.debug(f"investor logged in: {email}")

                        ma_schema = InvestorUserSchema()
                        user_objs = ma_schema.dump(user)
                        jwt_obj = {"email": email, "model": "Investor"}
                        access_token = create_access_token(identity=jwt_obj)
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
            else:
                return return_data_results(False, "invalid token", 400)
        except:
            return return_data_results(False, "token not validated", 400)
    else:
        return jsonify(response)


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
                user.is_logged_in = True
                user.save()
                logger.debug(f"investor logged in: {email}")

                ma_schema = InvestorUserSchema()
                user_objs = ma_schema.dump(user)
                jwt_obj = {"email": email, "model": "Investor"}
                access_token = create_access_token(identity=jwt_obj)
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
def reset_link(token):
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
            message = "password reset link sent"
            return return_data_results(True, message)
        else:
            return jsonify(response)

    elif request.method == "GET":
        message = "forgot password template"
        return return_data_results(True, message)


@investor_blueprint.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':

        input_request = request.get_json()
        response = validate_inv_first_page_schema(input_request)

        if response["result"]:
            email = response["data"]["email"]

            email_exist = Investor.objects.filter(email=email).first()

            if email_exist:
                logger.debug(f"investor exists: {email}")
                message = "email exists"
                return return_data_results(False, message)

            input_request["password"] = generate_password_hash(input_request["password"])
            new_user = Investor(**input_request)
            new_user.save()

            input_request["investor"] = True
            ml_schema = InvestorMLSchema()
            user = Investor.objects.filter(email=email).first()
            ml_schema_resp = ml_schema.dump(user)
            if not insert_into_matching(email, ml_schema_resp):
                pass
            # todo: shoot out a mail to angelfund team to get the data from investor db and dump it to matching db

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
@jwt_required
def update_info():
    jwt_decode = jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    user_obj = jwt_decode["user_obj"]
    if user_obj.is_logged_in:
        input_data = request.get_json()
        available_fields = {"sectors", "deals", "bio", "location", "prior_investment",
                            "accreditation", "syndicate", "angel", "profile_pic_link"}
        for field in input_data:
            if field in available_fields:
                setattr(user_obj, field, input_data[field])
            else:
                message = "invalid user field"
                return return_data_results(False, message)
        user_obj.save()
        if update_into_matching(user_obj.email, input_data):
            pass
            #todo: shoot out an email to the team
        ma_schema = InvestorUserSchema()
        user_objs = ma_schema.dump(user_obj)
        ret_obj = {
            "result": True,
            "user": user_objs,
        }
        return ret_obj
    else:
        message = "user is not authenticated"
        return return_data_results(False, message)


@investor_blueprint.route('/logout', methods=["POST"])
@jwt_required
def logout():
    jwt_decode = jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    user_obj = jwt_decode["user_obj"]
    user_obj.is_logged_in = False
    user_obj.save()
    return return_data_results(True, "user logged off")


@investor_blueprint.route('/referral-link', methods=["POST"])
@jwt_required
def referral_link():
    if request.method == "POST":
        jwt_decode = jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        user_obj = jwt_decode["user_obj"]
        inp_req = request.get_json()
        response = validate_referrer_schema(inp_req)

        if not response["result"]:
            return jsonify(response)

        ref_email = response["data"]["email"]
        refferred_to = list(user_obj.referred_to)
        refferred_to.append(ref_email)
        user_obj.referred_to = refferred_to
        user_obj.save()

        # shoutout mail to the respective person
        return jsonify({"result": True, "message": "mail sent"})


@investor_blueprint.route('/dashboard', methods=["GET", "POST"])
@jwt_required
def investors_dashboard():
    if request.method == "GET":
        jwt_decode = jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        user_obj = jwt_decode["user_obj"]
        matching_obj = get_matching_data(user_obj.email)

        if matching_obj == {}:
            return {} # no matching data as of now

        _id = matching_obj.get("_id")
        if not _id:
            #todo: shoot out a mail to the team to fix id in matching db
            return {} # temp display no matching startup

        discover = get_discover(_id)

        if not discover["result"]:
            # todo: shoot out a mail to the team to fix id in matching db
            return {}  # temp display no matching startup

        elif discover["result"] and discover["data"] == []:
            # todo: shoot out a mail to the team to fix id in matching db
            return {}  # temp display no matching startup

        else:
            str_data = process_all_str_data(discover["data"])
            return jsonify({"result": True, "data": str_data})

    elif request.method == "POST":
        jwt_decode = jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        inv_obj = jwt_decode["user_obj"]
        inv_email = inv_obj.email

        response = validate_dashboard_schema(request.get_json())
        if not response["result"]:
            return jsonify(response)

        str_email = response["data"]["email"]
        str_invite = response["data"]["invite"]

        if not str_invite:
            str_obj = Startup.objects.filter(email=str_email).first()
            str_feedback = response["data"]["feedback"]
            inv_passed_requests = dict(inv_obj.passed)
            str_feedback_requests = list(str_obj.feedback)
            inv_passed_requests[str_email] = True
            str_feedback["from_email"] = inv_email
            str_feedback_requests.append(str_feedback)
            inv_obj.passed = inv_passed_requests
            str_obj.feedback = str_feedback_requests
            inv_obj.save()
            str_obj.save()
            return jsonify({"result": True, "message": "passed"})

        if str_invite:
            str_obj = Startup.objects.filter(email=str_email).first()
            str_pending_requests = dict(str_obj.pending)
            str_connected_requests = dict(str_obj.connected)

            if str_pending_requests.get(inv_email):
                inv_connected_requests = dict(inv_obj.connected)
                str_pending_requests.pop(inv_email)
                str_connected_requests[inv_email] = True
                inv_connected_requests[str_email] = True
                inv_obj.connected = inv_connected_requests
                str_obj.connected = str_connected_requests
                str_obj.pending = str_pending_requests
                inv_obj.save()
                str_obj.save()
                return jsonify({"result": True, "message": "connected"})
                # todo: send email that they connected
            elif str_connected_requests.get(inv_email):
                return jsonify({"result": True, "message": "connected"})
            else:
                inv_pending_req = dict(inv_obj.pending)
                inv_pending_req[str_email] = True
                inv_obj.pending = inv_pending_req
                inv_obj.save()
                return jsonify({"result": True, "message": "invitation"})



@investor_blueprint.route('/ref/share/<token>', methods=["GET"])
def verify_referral_link(token):
    if token and len(token) == 10:
        hash_obj = ReferralLinks.objects.filter(hash_value=token).first()
        if hash_obj:
            referral_email = hash_obj.email
            return jsonify({
                "result": True,
                "message": "valid token",
                "referrer": referral_email
            })
        else:
            return return_data_results(False, "invalid token", 200)
    return return_data_results(False, "invalid token")


@investor_blueprint.route('/mime-files', methods=["POST"])
@jwt_required
def mime_files():
    jwt_decode = jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    user_obj = jwt_decode["user_obj"]

    file_name = None
    file_type = request.form.get("type")
    file_obj = request.files.get('file_obj')
    if file_obj:
        file_name = f"{user_obj.id}-" + file_obj.filename.replace(' ', '')
        file_name = file_name.split('.', 1)[0]

    if not all([file_obj, file_name, file_type]):
        return return_data_results(False, "missing key data")

    file_location = f"{os.getcwd()}/{str(uuid.uuid4())}"
    if os._exists(file_location):
        shutil.rmtree(file_location)

    os.mkdir(file_location)
    with open(f"{file_location}/{file_name}", 'wb') as f:
        f.write(file_obj.read())

    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(f"{file_location}/{file_name}")
    mime_base = mime_type.split('/',1)[0]        # base mime type :=> application (for pdf) or image (for image)
    mime_extention = mime_type.split('/', 1)[1]  # pdf or jpeg

    if file_type == "image":
        if mime_base == "image":
            image_url = profile_pic_upload_to_s3(file_name, mime_extention, file_location, file_name)
            user_obj.profile_pic_link = image_url
            user_obj.save()
            shutil.rmtree(file_location)
            return jsonify({"result": True, "url": image_url})
        else:
            shutil.rmtree(file_location)
            return return_data_results(False, "image file required")
    else:
        shutil.rmtree(file_location)
        return return_data_results(False, "invalid file type")


@investor_blueprint.route('/investor-common-mappings', methods=["GET"])
def investors_common_mapping():
    return get_common_mapping()


@investor_blueprint.route('/company-image-api', methods=["POST"])
@jwt_required
def general_company_images():
    if request.method == "POST":
        jwt_decode = jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        inp_req = request.get_json()
        response = validate_company_schema(inp_req)

        if not response["result"]:
            return jsonify(response)

        company_name = response["data"]["company_name"]
        return company_images_api(company_name)




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


def jwt_decoder(encoded_identifier):
    email = encoded_identifier["email"]
    model = encoded_identifier["model"]
    if model != "Investor":
        return {"result": False,
                "message": "invalid token"}
    user_obj = Investor.objects.filter(email=email).first()
    if not user_obj:
        return {"result": False,
                "message": "user not found"}
    return {
        "result": True,
        "user_obj": user_obj
    }