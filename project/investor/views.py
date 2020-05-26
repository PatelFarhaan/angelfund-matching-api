import os
import uuid
import magic
import shutil
import logging
import requests
import threading
from project import serial
from flask_login import login_user
from common_utilities import CONSTANT
from common_utilities.ml_apis import get_discover
from common_utilities.referral_email import email_referral
from common_utilities.jwt_decoder import investor_jwt_decoder
from common_utilities.connected_emails import email_connected
from common_utilities.company_images import company_images_api
from common_utilities.password_reset import password_reset_email
from flask import url_for, request, Blueprint, jsonify, redirect
from common_utilities.email_confirmation import email_confirmation
from common_utilities.google_email import google_email_confirmation
from common_utilities.get_inv_common_mappings import get_common_mapping
from common_utilities.mime_files_upload import profile_pic_upload_to_s3
from project.models import Investor, Startup, InvestorSubscriptionEmails
from werkzeug.security import generate_password_hash, check_password_hash
from common_utilities.common_mappings import sector_data, accreditation_data
from project.investor.marshmallow_serialize import InvestorUserSchema, InvestorMLSchema
from common_utilities.flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from project.startup.marshmallow_serialize import (StartupConnectedSchema, StartupPassedSchema, StartupDashboardSchema)
from common_utilities.investor_matching_db import (insert_into_matching, update_into_matching, get_matching_data, process_all_str_data)
from common_utilities.json_schema_investor_validation import (validate_inv_first_page_schema, validate_email_schema, validate_dashboard_schema,
validate_referrer_schema, validate_company_schema, validate_inv_passed_recvisit_schema, validate_google_schema, validate_inv_login_schema,
validate_inv_password_reset_schema, validate_inv_monday_notification_schema, validate_delete_acc_schema, validate_profile_vis_schema)


#<==================================================================================================>
#                                    LOGGER + BLUEPRINT
#<==================================================================================================>
logger = logging.getLogger(__name__)
investor_blueprint = Blueprint('investor', __name__, url_prefix='/api/v1/investor',  template_folder="templates")


#<==================================================================================================>
#                                   GOOGLE SIGNUP AND SIGNIN
#<==================================================================================================>
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
                        if getattr(user, "delete_account"):
                            return jsonify({"result": False, "message": "account deleted"})

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
                        new_user = Investor(**user_dict)
                        new_user.save()

                        user = InvestorSubscriptionEmails.objects.filter(email=email).first()
                        if user:
                            user.delete()

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


#<==================================================================================================>
#                                            LOGIN
#<==================================================================================================>
@investor_blueprint.route('/login', methods=['POST'])
def login():
    input_request = request.get_json()
    response = validate_inv_login_schema(input_request)
    if response["result"]:
        email = response["data"]["email"]
        password = response["data"]["password"]

        user = Investor.objects.filter(email=email).first()
        if user is None:
            error = "user does not exist"
            logger.debug(f"investor does not exixt: {email}")
            return jsonify({"result": False, "error": error})

        if user.is_google_signup:
            return_obj = {
                "status_code": 200,
                "message": "registered with google account",
                "redirect_url": "https://127.0.0.1:5000/investor/login/callback"
            }
            return jsonify(return_obj)

        if not user.email_confirmed:
            error = "email address not verified"
            token = serial.dumps(email, salt='email_confirm')
            link = url_for('investor.email_confirmed', token=token, _external=True)
            thread = threading.Thread(target=email_confirmation, args=(email, link, user.first_name))
            thread.start()
            return jsonify({"result": False, "error": error})

        if user and check_password_hash(user.password, password):
            if getattr(user, "delete_account"):
                return jsonify({"result": False, "error": "account deleted"})

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
            error = "wrong credentails"
            return jsonify({"result": False, "error": error})
    else:
        return jsonify(response)


#<==================================================================================================>
#                                      PASSWORD RESET LINK
#<==================================================================================================>
@investor_blueprint.route('/reset-link/<token>', methods=['POST'])
def reset_link(token):
    try:
        email = serial.loads(token, salt='email_reset', max_age=int(CONSTANT.PASSWORD_RESET_LINK_AGE.value))
    except:
        return redirect("https://www.angelfund.ai/token-expired", code=302)

    user = Investor.objects.filter(email=email).first()
    if user:
        input_request = request.get_json()
        response = validate_inv_password_reset_schema(input_request)
        if response["result"]:
            password = response["data"]["password"]

            if user.password_reset_meta_data == {}:
                return jsonify({"result": False, "error": "link can be used only once"})

            if not user.password_reset_meta_data["is_clicked"]:
                user.password = generate_password_hash(password)
                user.password_reset_meta_data = {}
                user.save()
                logger.debug(f"investor password changed: {email}")
                message = "password changed successfully"
                return jsonify({"result": True, "message": message})
        else:
            return jsonify(response)


#<==================================================================================================>
#                               PASSWORD RESET REQUEST (HOMEPAGE)
#<==================================================================================================>
@investor_blueprint.route('/forgot-password', methods=['POST'])
def forgot_password():
    input_request = request.get_json()
    response = validate_email_schema(input_request)
    if response["result"]:
        email = response["data"]["email"]
        user = Investor.objects.filter(email=email).first()

        if user is None:
            logger.debug(f"investor does not exist: {email}")
            return jsonify({"result": True, "message": "email sent if the user exists"})

        token = serial.dumps(user.email, salt='email_reset')
        link = url_for('investor.reset_link', token=token, _external=True)
        user.password_reset_meta_data = {"is_clicked": False}
        user.save()

        thread = threading.Thread(target=password_reset_email, args=(email, link,))
        thread.start()
        logger.debug(f"investor password reset link sent: {email}")
        return jsonify({"result": True, "message": "email sent if the user exists"})
    else:
        return jsonify(response)


#<==================================================================================================>
#                                          REGISTER
#<==================================================================================================>
@investor_blueprint.route('/register', methods=['POST'])
def register():
    input_request = request.get_json()
    response = validate_inv_first_page_schema(input_request)

    if response["result"]:
        email = response["data"]["email"]

        email_exist = Investor.objects.filter(email=email).first()

        if email_exist:
            logger.debug(f"investor exists: {email}")
            error = "email exists"
            return jsonify({"result": False, "error": error})

        input_request["password"] = generate_password_hash(input_request["password"])
        new_user = Investor(**input_request)
        new_user.save()

        ml_schema = InvestorMLSchema()
        user = Investor.objects.filter(email=email).first()
        ml_schema_resp = ml_schema.dump(user)

        if not insert_into_matching(email, ml_schema_resp):
            pass
            # todo: shoot out a mail to angelfund team to get the data from investor db and dump it to matching db

        logger.debug(f"investor created {email}")

        token = serial.dumps(email, salt='email_confirm')
        link = url_for('investor.email_confirmed', token=token, _external=True)
        thread = threading.Thread(target=email_confirmation, args=(email, link, input_request.get("first_name")))
        thread.start()
        message = "investor created"
        return jsonify({"result": True, "message": message})
    else:
        return jsonify(response)


#<==================================================================================================>
#                                   EMAIL CONFIRMATION TOKEN
#<==================================================================================================>
@investor_blueprint.route('/email-confirmed/<token>', methods=['GET'])
def email_confirmed(token):
    try:
        email = serial.loads(token, salt='email_confirm')
    except:
        return redirect("https://www.angelfund.ai/token-expired", code=302)

    user = Investor.objects.filter(email=email).first()

    if user:
        user.email_confirmed = True
        user.save()

        if update_into_matching(email, {"email_confirmed": True}):
            pass
            # todo: shoot out an email to the team with the user email as the subject header

        logger.debug(f"investor email confirmed {email}")
        return redirect("https://www.angelfund.ai", code=302)
    else:
        logger.debug(f"investor does not exist {email}")
        return redirect("https://www.angelfund.ai/no-user-found", code=302)


#<==================================================================================================>
#                                          LOGOUT
#<==================================================================================================>
@investor_blueprint.route('/logout', methods=["POST"])
@jwt_required
def logout():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    user_obj = jwt_decode["user_obj"]
    user_obj.is_logged_in = False
    user_obj.save()
    return jsonify({"result": True, "message": "user logged out"})


#<==================================================================================================>
#                                      REFERRAL LINK
#<==================================================================================================>
@investor_blueprint.route('/referral-link', methods=["POST"])
@jwt_required
def referral_link():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
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

    full_name = user_obj.first_name + " " + user_obj.last_name
    first_name = user_obj.first_name

    email_referral(ref_email, full_name, first_name)
    return jsonify({"result": True, "message": "mail sent"})


#<==================================================================================================>
#                                      UPDATE INFORMATION
#<==================================================================================================>
@investor_blueprint.route('/update-info', methods=['PATCH'])
@jwt_required
def update_info():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    user_obj = jwt_decode["user_obj"]
    if user_obj.is_logged_in:
        input_data = request.get_json()
        available_fields = {"sectors", "deals", "bio", "location", "prior_investments",
                            "accreditation", "syndicate", "angel", "profile_pic_link"}
        for field in input_data:
            if field in available_fields:
                if field == "sectors":
                    sectors_map = sector_data()
                    res = [ sectors_map.get(i) for i in input_data[field] if sectors_map.get(i) != None ]
                    setattr(user_obj, field, res)

                    if update_into_matching(user_obj.email, {field: res}):
                        pass
                        # todo: shoot out an email to the team with the user email as the subject header

                elif field == "accreditation":
                    accreditation_map = accreditation_data()
                    res = accreditation_map.get(input_data[field])
                    setattr(user_obj, field, res)

                    if update_into_matching(user_obj.email, {field: res}):
                        pass
                        # todo: shoot out an email to the team with the user email as the subject header

                else:
                    setattr(user_obj, field, input_data[field])
                    if update_into_matching(user_obj.email, {field: input_data[field]}):
                        pass
                        # todo: shoot out an email to the team with the user email as the subject header

                user_obj.save()

            else:
                message = "invalid user field"
                return return_data_results(False, message)

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





#########      TEST ONCE ONBOARDING FLOW IS COMPLETED        #########






@investor_blueprint.route('/mime-files', methods=["POST"])
@jwt_required
def mime_files():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
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


@investor_blueprint.route('/dashboard', methods=["GET", "POST"])
@jwt_required
def investors_dashboard():
    if request.method == "GET":
        jwt_decode = investor_jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        user_obj = jwt_decode["user_obj"]
        matching_obj = get_matching_data(user_obj.email)

        if matching_obj == {}:
            return {"result": False, "message": "no match found"}

        _id = matching_obj.get("_id")

        if not _id:
            return {"result": False, "message": "no id found"}

        discover = get_discover(_id)

        if not discover["result"]:
            return {"result": False, "message": "no match found"}

        elif discover["result"] and discover["data"] == []:
            return {"result": False, "message": "no match found"}

        else:
            str_data = process_all_str_data(discover["data"])
            return jsonify({"result": True, "data": str_data})

    elif request.method == "POST":
        jwt_decode = investor_jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        inv_obj = jwt_decode["user_obj"]
        inv_email = inv_obj.email

        response = validate_dashboard_schema(request.get_json())
        if not response["result"]:
            return jsonify(response)


        str_email = response["data"]["email"]
        str_invite = response["data"]["invite"]

        if inv_obj.connected.get(str_email):
            return jsonify({"result": False, "message": "already connected"})

        if not str_invite:
            str_obj = Startup.objects.filter(email=str_email).first()

            if not response["data"].get("feedback"):
                return jsonify({"result": False, "message": "feedback is mandotory"})

            str_feedback = response["data"]["feedback"]

            str_feedback_requests = dict(str_obj.feedback)
            str_feedback_requests[inv_email] = str_feedback
            str_obj.feedback = str_feedback_requests

            inv_passed_requests = dict(inv_obj.passed)
            inv_passed_requests[str_email] = True
            inv_obj.passed = inv_passed_requests

            inv_pending_requests = dict(inv_obj.pending)
            if inv_pending_requests.get(str_email):
                inv_pending_requests.pop(str_email)
            inv_obj.pending = inv_pending_requests

            inv_connected_requests = dict(inv_obj.connected)
            if inv_connected_requests.get(str_email):
                inv_connected_requests.pop(str_email)
            inv_obj.connected = inv_connected_requests

            inv_obj.save()
            str_obj.save()
            return jsonify({"result": True, "message": "passed"})

        if str_invite:
            str_obj = Startup.objects.filter(email=str_email).first()
            str_pending_requests = dict(str_obj.pending)

            if str_pending_requests.get(inv_email):

                inv_pending_requests = dict(inv_obj.pending)
                if inv_pending_requests.get(str_email):
                    inv_pending_requests.pop(str_email)
                inv_obj.pending = inv_pending_requests

                inv_passed_requests = dict(inv_obj.passed)
                if inv_passed_requests.get(str_email):
                    inv_passed_requests.pop(str_email)
                inv_obj.passed = inv_passed_requests

                str_pending_requests = dict(str_obj.pending)
                if str_pending_requests.get(inv_email):
                    str_pending_requests.pop(inv_email)
                str_obj.pending = str_pending_requests

                str_passed_requests = dict(str_obj.passed)
                if str_passed_requests.get(inv_email):
                    str_passed_requests.pop(inv_email)
                str_obj.passed = str_passed_requests

                inv_connected_requests = dict(inv_obj.connected)
                inv_connected_requests[str_email] = True
                inv_obj.connected = inv_connected_requests

                str_connected_requests = dict(str_obj.connected)
                str_connected_requests[inv_email] = True
                str_obj.connected = str_connected_requests

                inv_obj.save()
                str_obj.save()

                deals = {
                        "0": "$25,000 to $50,000",
                        "1": "$50,000 to $100,000",
                        "2": "$100,000 to $250,000",
                        "3": "$250,000 to $500,000"
                    }

                temp_dict = {}
                temp_dict["inv_bio"] = inv_obj.bio
                # temp_dict["inv_deals"] = deals.get(inv_obj.deals)
                temp_dict["inv_deals"] = list(deals.get(inv_obj.deals))[0]
                temp_dict["inv_fn"] = inv_obj.first_name

                if inv_obj.profile_pic_link:
                    temp_dict["inv_img"] = inv_obj.profile_pic_link
                else:
                    temp_dict["inv_img"] = CONSTANT.ANONYMOUS_PP.value

                temp_dict["str_bio"] = str_obj.bio
                temp_dict["str_fn"] = str_obj.first_name
                if str_obj.co_founders != []:
                    temp_dict["str_founders"] = str_obj.co_founders[0].get("name")
                    if str_obj.co_founders[0].get("position") != []:
                        temp_dict["str_position"] = str_obj.co_founders[0].get("position")[0]
                    else:
                        temp_dict["str_founders"] = None
                else:
                    temp_dict["str_founders"] = None
                    temp_dict["str_position"] = None

                temp_dict["str_seeking"] = str_obj.round_size
                temp_dict["str_raised"] = str_obj.raised
                if str_obj.profile_pic_link:
                    temp_dict["str_img"] = str_obj.profile_pic_link
                else:
                    temp_dict["str_img"] = CONSTANT.ANONYMOUS_PP.value

                email_connected(inv_email, str_email, temp_dict)

                return jsonify({"result": True, "message": "connected"})

            else:
                inv_passed_requests = dict(inv_obj.passed)
                if inv_passed_requests.get(str_email):
                    inv_passed_requests.pop(str_email)
                inv_obj.passed = inv_passed_requests

                inv_pending_req = dict(inv_obj.pending)
                inv_pending_req[str_email] = True
                inv_obj.pending = inv_pending_req

                inv_obj.save()
                return jsonify({"result": True, "message": "invitation"})


@investor_blueprint.route('/history-all', methods=["GET"])
@jwt_required
def history():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    inv_obj = jwt_decode["user_obj"]
    data = []

    # passed
    passed = getattr(inv_obj, "passed")
    ma_schema = StartupPassedSchema()
    for k, v in passed.items():
        str_obj = Startup.objects.filter(email=k).first()
        data.append(ma_schema.dump(str_obj))

    # connected
    connected = getattr(inv_obj, "connected")
    ma_schema = StartupConnectedSchema()
    for k, v in connected.items():
        str_obj = Startup.objects.filter(email=k).first()
        data.append(ma_schema.dump(str_obj))

    return jsonify({"result": True, "data": data})


@investor_blueprint.route('/history-connected', methods=["GET"])
@jwt_required
def connected():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    inv_obj = jwt_decode["user_obj"]
    connected = getattr(inv_obj, "connected")
    ma_schema = StartupConnectedSchema()
    data = []
    for k,v in connected.items():
        str_obj = Startup.objects.filter(email=k).first()
        data.append(ma_schema.dump(str_obj))
    return jsonify({"result": True, "data": data})


@investor_blueprint.route('/history-passed', methods=["GET"])
@jwt_required
def passed():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    inv_obj = jwt_decode["user_obj"]
    passed = getattr(inv_obj, "passed")
    ma_schema = StartupPassedSchema()
    data = []
    for k, v in passed.items():
        str_obj = Startup.objects.filter(email=k).first()
        data.append(ma_schema.dump(str_obj))
    return jsonify({"result": True, "data": data})


@investor_blueprint.route('/history-passed-revisit', methods=["POST"])
@jwt_required
def passed_revisit():
    if request.method == "POST":
        input_req = request.get_json()
        response = validate_inv_passed_recvisit_schema(input_req)

        if response["result"]:
            email = response["data"]["email"]
            str_obj = Startup.objects.filter(email=email).first()
            if not str_obj:
                return jsonify({"result": False, "data": None})

            ma_schema = StartupDashboardSchema()
            data = ma_schema.dump(str_obj)
            return jsonify({"result": True, "data": data})
        else:
            return jsonify(response)


@investor_blueprint.route('/monday-notifications', methods=["POST"])
@jwt_required
def monday_notifications():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    inv_obj = jwt_decode["user_obj"]

    if request.method == "POST":
        response = validate_inv_monday_notification_schema(request.get_json())
        if response["result"]:
            setattr(inv_obj,"monday_notification", response["data"]["monday_notification"])
            inv_obj.save()
            return jsonify({"result": True, "message": "value updated"})
        else:
            return jsonify(response)


@investor_blueprint.route('/investor-common-mappings', methods=["GET"])
def investors_common_mapping():
    return get_common_mapping()


@investor_blueprint.route('/company-image-api', methods=["POST"])
@jwt_required
def general_company_images():
    if request.method == "POST":
        jwt_decode = investor_jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        inp_req = request.get_json()
        response = validate_company_schema(inp_req)

        if not response["result"]:
            return jsonify(response)

        company_name = response["data"]["company_name"]
        return company_images_api(company_name)


@investor_blueprint.route('/delete-account', methods=["POST"])
@jwt_required
def delete_account():
    if request.method == "POST":
        jwt_decode = investor_jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        inv_obj = jwt_decode["user_obj"]
        response = validate_delete_acc_schema(request.get_json())
        if response["result"]:
            password = response["data"]["password"]
            if check_password_hash(inv_obj.password, password):
                setattr(inv_obj, "delete_account", True)
                inv_obj.save()
                return jsonify({"result": True, "message": "account deleted"})
            return jsonify({"result": False, "message": "wrong credentials"})
        return jsonify(response)


@investor_blueprint.route('/profile-visibility', methods=["POST"])
@jwt_required
def profile_visibility():
    if request.method == "POST":
        jwt_decode = investor_jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        inv_obj = jwt_decode["user_obj"]
        response = validate_profile_vis_schema(request.get_json())
        if response["result"]:
            visible = response["data"]["visible"]
            setattr(inv_obj, "show_profile", visible)
            inv_obj.save()
            return jsonify({"result": True, "message": "value updated"})
        return jsonify(response)


@investor_blueprint.route('/subscription', methods=["POST"])
def subscription_email():
    if request.method == "POST":
        inp_req = request.get_json()
        response = validate_email_schema(inp_req)
        if response["result"]:
            email = response["data"]["email"]
            inv_obj = InvestorSubscriptionEmails.objects.filter(email=email).first()

            if inv_obj is not None:
                return jsonify({"result": False, "error": "Email already exists"})

            new_obj = InvestorSubscriptionEmails(email=email)
            new_obj.save()
            return jsonify({"result": True})

        return jsonify(response)

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