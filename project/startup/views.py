#<==================================================================================================>
#                                            IMPORTS
#<==================================================================================================>
import os
import uuid
import magic
import shutil
import logging
import requests
import threading
from project import serial
from common_utilities import CONSTANT
from flask_login import login_user, login_required
from project.models import Startup, Investor, Referrals
from common_utilities.jwt_decoder import startup_jwt_decoder
from common_utilities.emails.referral_email import email_referral
from common_utilities.technical_error_mail import technical_errors
from common_utilities.emails.connected_emails import email_connected
from common_utilities.emails.password_reset import password_reset_email
from werkzeug.security import generate_password_hash, check_password_hash
from common_utilities.emails.email_confirmation import email_confirmation
from common_utilities.emails.wait_list_email_str import wait_list_user_str
from common_utilities.emails.google_email import google_email_confirmation
from common_utilities.emails.account_delete_email import delete_user_account
from common_utilities.analytics.user_signin_analytics import login_analytics
from common_utilities.analytics.user_signup_analytics import signup_analytics
from project.startup.marshmallow_serialize import StartupUserSchema, StartupMLSchema
from common_utilities.common_mappings import sector_data, progress_mapping, round_def
from common_utilities.json_schema_investor_validation import validate_referrer_schema
from common_utilities.machine_learning.hide_user_profile import hide_user, unhide_user
from common_utilities.mime_files_upload import profile_pic_upload_to_s3, pdf_upload_to_s3
from common_utilities.reverse_common_mapping import rev_sector_data, rev_progress_mapping
from flask import url_for, request, session, Blueprint, jsonify, redirect, render_template
from common_utilities.flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from common_utilities.machine_learning.investor_matching_db import inv_mutual_updates, get_inv_matching_data
from project.investor.marshmallow_serialize import InvestorConnectedSchema, InvestorFeedbackSchema, InvestorDashboardSchema
from common_utilities.json_schema_investor_validation import validate_inv_passed_recvisit_schema, validate_delete_acc_conf_schema
from common_utilities.machine_learning.ml_apis import get_discover, set_response, delete_user_ml, reset_settings, hide_profile_from_discover
from common_utilities.machine_learning.startup_matching_db import insert_into_matching, update_into_matching, get_str_matching_data, process_all_str_data, \
    str_mutual_updates
from common_utilities.json_schema_startup_validation import (validate_str_first_page_schema, validate_dashboard_schema, validate_str_monday_notification_schema,
                                                             validate_referrer_schema, validate_delete_acc_schema, validate_google_schema, validate_str_login_schema,
                                                             validate_email_schema, validate_profile_vis_schema, validate_remove_slide_deck_schema)


#<==================================================================================================>
#                                     LOGGER + BLUEPRINT
#<==================================================================================================>
logger = logging.getLogger(__name__)
startup_blueprint = Blueprint('startup', __name__, url_prefix='/api/v1/startup')


#<==================================================================================================>
#                                    GOOGLE SIGNUP AND SIGNIN
#<==================================================================================================>
@startup_blueprint.route("/google-token", methods=["POST"])
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
                    if email:
                        email = email.lower()

                    user = Startup.objects.filter(email=email).first()
                    if user:
                        login_user(user)
                        user.is_logged_in = True
                        user.save()
                        logger.debug(f"startup: google-token: logged in: {email}")

                        ma_schema = StartupUserSchema()
                        user_objs = ma_schema.dump(user)

                        analytics_thread = threading.Thread(target=login_analytics, args=(email, False,))
                        analytics_thread.start()

                        rev_sectors_data = rev_sector_data()
                        rev_progress_data = rev_progress_mapping()

                        user_objs["progress"] = [rev_progress_data.get(i) for i in user_objs["progress"] if rev_progress_data.get(i)]
                        user_objs["sectors"] = [rev_sectors_data.get(i) for i in user_objs["sectors"] if rev_sectors_data.get(i)]

                        jwt_obj = {"email": email, "model": "Startup"}
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

                        user_dict = dict(email=email,
                                         last_name=last_name,
                                         email_confirmed=True,
                                         first_name=first_name,
                                         is_google_signup=True,
                                         profile_pic_link=picture)

                        # noinspection PyArgumentList
                        new_user = Startup(**user_dict)
                        new_user.save()

                        ml_schema = StartupMLSchema()
                        user = Startup.objects.filter(email=email).first()
                        ml_schema_resp = ml_schema.dump(user)
                        if not insert_into_matching(email, ml_schema_resp):
                            technical_errors("STARTUP: SIGNUP FLOW UPDATE UNSUCCESSFUL", email)

                        logger.debug(f"startup: google-token: created via Google OAuth: {email}")

                        thread = threading.Thread(target=google_email_confirmation, args=(user,))
                        thread.start()

                        user = Startup.objects.filter(email=email).first()
                        login_user(user)
                        user.is_logged_in = True
                        user.save()
                        logger.debug(f"startup: google-token: logged in: {email}")

                        ma_schema = StartupUserSchema()
                        user_objs = ma_schema.dump(user)

                        signup_analytics_thread = threading.Thread(target=signup_analytics, args=(False,))
                        signup_analytics_thread.start()

                        rev_sectors_data = rev_sector_data()
                        rev_progress_data = rev_progress_mapping()

                        user_objs["progress"] = [rev_progress_data.get(i) for i in user_objs["progress"] if rev_progress_data.get(i)]
                        user_objs["sectors"] = [rev_sectors_data.get(i) for i in user_objs["sectors"] if rev_sectors_data.get(i)]

                        jwt_obj = {"email": email, "model": "Startup"}
                        access_token = create_access_token(identity=jwt_obj)
                        ret_obj = {
                            "result": True,
                            "user": user_objs,
                            "token": access_token,
                        }
                        return ret_obj
                else:
                    message = "User email not available or not verified by Google."
                    logger.debug(f"startup: google-token: {message}: {userinfo_response.json().get('email', 'email_not_mentioned')}")
                    return jsonify({"result": False, "error": message}), 400
            else:
                return jsonify({"result": False, "error": "invalid token"}), 400
        except:
            return jsonify({"result": False, "error": "token not validated"}), 400
    else:
        return jsonify(response)


#<==================================================================================================>
#                                           LOGIN
#<==================================================================================================>
@startup_blueprint.route('/login', methods=['POST'])
def login():
    input_request = request.get_json()
    response = validate_str_login_schema(input_request)
    if response["result"]:
        email = response["data"]["email"]
        password = response["data"]["password"]

        if email:
            email = email.lower()

        user = Startup.objects.filter(email=email).first()
        if user is None:
            error = "user does not exist"
            logger.debug(f"startup: login: does not exist: {email}")
            return jsonify({"result": False, "error": error})

        if user.is_google_signup:
            return_obj = {
                "result": False,
                "error": "registered with google account",
            }
            return jsonify(return_obj)

        if not user.email_confirmed:
            error = "please confirm your email address"
            token = serial.dumps(email, salt='email_confirm')
            link = url_for('startup.email_confirmed', token=token, _external=True)
            thread = threading.Thread(target=email_confirmation, args=(email, link, user.first_name))
            thread.start()
            return jsonify({"result": False, "error": error})

        if user and check_password_hash(user.password, password):
            if getattr(user, "delete_account"):
                return jsonify({"result": False, "error": "account deleted"})

            login_user(user)
            user.is_logged_in = True
            user.save()
            logger.debug(f"startup: login: logged in: {email}")

            analytics_thread = threading.Thread(target=login_analytics, args=(email, False,))
            analytics_thread.start()

            ma_schema = StartupUserSchema()
            user_objs = ma_schema.dump(user)

            rev_sectors_data = rev_sector_data()
            rev_progress_data = rev_progress_mapping()

            user_objs["progress"] = [rev_progress_data.get(i) for i in user_objs["progress"] if rev_progress_data.get(i)]
            user_objs["sectors"] = [rev_sectors_data.get(i) for i in user_objs["sectors"] if rev_sectors_data.get(i)]

            jwt_obj = {"email": email, "model": "Startup"}
            access_token = create_access_token(identity=jwt_obj)
            ret_obj = {
                "result": True,
                "user": user_objs,
                "token": access_token
            }
            return ret_obj
        else:
            logger.debug(f"startup: login: wrong credentials: {email}")
            return jsonify({"result": False, "error": "wrong credentials"})
    else:
        return jsonify(response)


#<==================================================================================================>
#                                    PASSWORD RESET LINK
#<==================================================================================================>
@startup_blueprint.route('/reset-link/<token>', methods=['GET', 'POST'])
def reset_link(token):
    if request.method == "GET":
        return render_template("reset.html")

    elif request.method == "POST":
        try:
            email = serial.loads(token, salt='email_reset', max_age=int(CONSTANT.PASSWORD_RESET_LINK_AGE.value))
            logger.debug(f"startup: reset-link/token: reset password link clicked: {email}")
            if email:
                user_obj = Startup.objects.filter(email=email).first()
                user_obj.is_logged_in = False
                user_obj.save()
                logger.debug(f"startup: reset-link/token: user logged out: {email}")
                email = email.lower()
        except:
            return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)

        user = Startup.objects.filter(email=email).first()
        if user:
            password = request.form.get("password")

            if user.password_reset_meta_data == {}:
                return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)

            if not user.password_reset_meta_data["is_clicked"]:
                user.password = generate_password_hash(password)
                user.password_reset_meta_data = {}
                user.save()
                logger.debug(f"startup: reset-link/token: password changed: {email}")
                return render_template("reset-success-str.html")
        else:
            logger.debug(f"startup: reset-link/token: user does not exist: {email}")
            return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)


#<==================================================================================================>
#                                         REGISTER
#<==================================================================================================>
@startup_blueprint.route('/register', methods=['POST'])
def register():
    input_request = request.get_json()
    response = validate_str_first_page_schema(input_request)

    if response["result"]:
        email = response["data"]["email"]
        if email:
            email = email.lower()

        email_exist = Startup.objects.filter(email=email).first()

        if email_exist:
            logger.debug(f"startup: register: exists: {email}")
            error = "email exists"
            return jsonify({"result": False, "error": error})

        input_request["password"] = generate_password_hash(input_request["password"])

        input_request["co_founders"] = [
            {
                "primary": True,
                "name": f"{input_request['first_name']} {input_request['last_name']}",
                "position": [None],
                "bio": None,
                "linkedin_link": None,
                "profile_image": None
            }
        ]

        new_user = Startup(**input_request)
        new_user.save()

        ml_schema = StartupMLSchema()
        user = Startup.objects.filter(email=email).first()
        ml_schema_resp = ml_schema.dump(user)

        if not insert_into_matching(email, ml_schema_resp):
            technical_errors("STARTUP: REGISTER FLOW UPDATE UNSUCCESSFUL", email)

        logger.debug(f"startup: register: created {email}")

        token = serial.dumps(email, salt='email_confirm')
        link = url_for('startup.email_confirmed', token=token, _external=True)
        thread = threading.Thread(target=email_confirmation, args=(email, link, user.first_name))
        thread.start()

        signup_analytics_thread = threading.Thread(target=signup_analytics, args=(False,))
        signup_analytics_thread.start()

        user.passowrd_confirm_meta_data = {"is_clicked": False}
        user.save()

        message = "startup created"
        return jsonify({"result": True, "message": message})
    else:
        return jsonify(response)


#<==================================================================================================>
#                                   EMAIL CONFIRMATION TOKEN
#<==================================================================================================>
@startup_blueprint.route('/email-confirmed/<token>', methods=['GET'])
def email_confirmed(token):
    try:
        email = serial.loads(token, salt='email_confirm')
        logger.debug(f"startup: email-confirmed: email confirmation link clicked: {email}")
        if email:
            email = email.lower()
    except:
        return redirect(f"{CONSTANT.CURRENT_SERVER.value}/login", code=302)

    user = Startup.objects.filter(email=email).first()

    if user:
        if user.passowrd_confirm_meta_data == {}:
            return redirect(f"{CONSTANT.CURRENT_SERVER.value}/login", code=302)
        else:
            user.email_confirmed = True
            user.save()
            logger.debug(f"startup: email-confirmed: email confirmed: {email}")

        if not update_into_matching(email, {"email_confirmed": True}):
            technical_errors("STARTUP: EMAIL CONFIRMED UPDATE UNSUCCESSFUL", email)

        login_user(user)
        user.is_logged_in = True
        user.passowrd_confirm_meta_data = {}
        user.save()
        session["email"] = email

        logger.debug(f"startup: email-confirmed: logged in: {email}")
        return redirect(url_for("startup.confirmation_signup_flow", email=email, code=307))

    else:
        logger.debug(f"startup: email-confirmed: user does not exist {email}")
        return redirect(f"{CONSTANT.CURRENT_SERVER.value}/login", code=302)


#<==================================================================================================>
#                                  CONFIRMATION SIGNUP FLOW
#<==================================================================================================>
@startup_blueprint.route('/confirmation-signup-flow', methods=["GET"])
@login_required
def confirmation_signup_flow():
    email = session.get("email")

    if email:
        email = email.lower()

    if not email:
        logger.debug(f"startup: confirmation-signup-flow: email not in session: {email}")
        return jsonify({"reuslt": False, "error": "session expired"})

    str_obj = Startup.objects.filter(email=email).first()
    first_name = (str_obj.first_name).strip().replace(" ", "_")
    last_name = (str_obj.last_name).strip().replace(" ", "_")
    query_string = f"confirmed=True&email={str_obj.email}&fn={first_name}&ln={last_name}&investor=false"
    logger.debug(f"startup: confirmation-signup-flow: redirect to onboarding flow: {email}")
    return redirect(f"{CONSTANT.CURRENT_SERVER.value}/startup/signup?{query_string}"), 302


#<==================================================================================================>
#                                          LOGOUT
#<==================================================================================================>
@startup_blueprint.route('/logout', methods=["POST"])
@jwt_required
def logout():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    user_obj = jwt_decode["user_obj"]

    user_obj.is_logged_in = False
    user_obj.save()
    logger.debug(f"startup: logout: user logged out: {user_obj.email}")
    return jsonify({"result": True, "message": "user logged out"})


#<==================================================================================================>
#                                       REFERRAL LINK
#<==================================================================================================>
@startup_blueprint.route('/referral-link', methods=["POST"])
@jwt_required
def referral_link():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    user_obj = jwt_decode["user_obj"]

    inp_req = request.get_json()
    response = validate_referrer_schema(inp_req)

    if not response["result"]:
        return jsonify(response)

    ref_email = response["data"]["email"]
    if ref_email:
        ref_email = ref_email.lower()

    if Investor.objects.filter(email=ref_email).first():
        logger.debug(f"startup: referral-link: referral email exists on investors model: {ref_email}")
        return jsonify({"result": False, "error": "user exists"})

    if Startup.objects.filter(email=ref_email).first():
        logger.debug(f"startup: referral-link: referral email exists on startup model: {ref_email}")
        return jsonify({"result": False, "error": "user exists"})

    full_name = user_obj.first_name + " " + user_obj.last_name
    first_name = user_obj.first_name

    ref_obj = {"referred_by": user_obj.email, "referred": ref_email}
    logger.info(f"startup: referral-link: {ref_email} is referred by {user_obj.email}")

    token = serial.dumps(ref_obj, salt='email_referral')
    link = url_for('startup.referral_verification', token=token, _external=True)
    thread = threading.Thread(target=email_referral,
                              args=((ref_email, full_name, first_name, link, "startup",
                                     CONSTANT.CURRENT_SERVER.value)))
    thread.start()
    return jsonify({"result": True, "message": "mail sent"})


#<==================================================================================================>
#                                  REFERRAL VERIFICATION
#<==================================================================================================>
@startup_blueprint.route('/referral/<token>', methods=["GET"])
def referral_verification(token):
    try:
        ref_obj = serial.loads(token, salt='email_referral')
        referred_by = ref_obj.get("referred_by")
        referred = ref_obj.get("referred")
    except:
        return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)

    user = Startup.objects.filter(email=referred_by).first()

    if user:
        # For referred_by user
        ref_by_obj = Referrals.objects.filter(email=user.email).first()
        if ref_by_obj:
            details = dict(ref_by_obj.details)
            referred_to = list(details.get("referred_to"))
            if referred in referred_to:
                logger.debug(f"startup: referral: {referred} is already referred by {referred_by}")
                return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)

            referred_to.append(referred)
            details["referred_to"] = referred_to
            ref_by_obj.details = details
            ref_by_obj.save()
        else:
            details = {
                "referred_by": None,
                "referred_to": [referred]
            }
            new_ref_obj = Referrals(email=referred_by, details=details)
            new_ref_obj.save()

        # For referred_to user
        ref_to_obj = Referrals.objects.filter(email=referred).first()
        if ref_to_obj:
            logger.debug(f"startup: referral: {referred} is already referred by {referred_by}")
            return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)

        details = {
            "referred_by": referred_by,
            "referred_to": []
        }
        new_ref_obj = Referrals(email=referred, details=details)
        new_ref_obj.save()

        logger.debug(f"startup: referral: {referred} is referred by {referred_by}")
        return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)
    else:
        logger.debug(f"startup: referral: startup does not exist {referred_by}")
        return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)


#<==================================================================================================>
#                                         UPDATE INFORMATION
#<==================================================================================================>
@startup_blueprint.route('/update-info', methods=['PATCH'])
@jwt_required
def update_info():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    user_obj = jwt_decode["user_obj"]

    if user_obj.is_logged_in:
        input_data = request.get_json()
        available_fields = {"location", "sectors", "company_name", "company_link", "co_founders",
                            "startup_pitch", "bio", "round_size", "raised", "profile_pic_link",
                            "progress", "position", "num_team_members", "slide_deck", "first_invite",
                            "first_dashboard_visit"}

        for key in list(input_data.keys()):
            if key not in available_fields:
                logger.debug(f"startup: update-info: {key} key does not exist in available fields: {user_obj.email}")
                return jsonify({"result": False, "error": "invalid user field"})

        for field in input_data:
            if field in available_fields:

                if field == "sectors":
                    sectors_map = sector_data()
                    res = [ sectors_map.get(i) for i in input_data[field] if sectors_map.get(i) != None ]
                    setattr(user_obj, field, res)
                    logger.info(f"startup: update-info: {field } updated to {res}: {user_obj.email}")

                    if not update_into_matching(user_obj.email, {field: res}):
                        technical_errors("STARTUP: SECTORS DATA UPDATE UNSUCCESSFUL", user_obj.email)

                elif field == "progress":
                    progress_map = progress_mapping()
                    res = [ progress_map.get(i) for i in input_data[field] if progress_map.get(i) != None ]
                    setattr(user_obj, field, res)
                    logger.info(f"startup: update-info: {field} updated to {res}: {user_obj.email}")

                    if not update_into_matching(user_obj.email, {field: res}):
                        technical_errors("STARTUP: PROGRESS DATA UPDATE UNSUCCESSFUL", user_obj.email)

                elif field == "round_size":
                    setattr(user_obj, field, input_data[field])
                    logger.info(f"startup: update-info: {field} updated to {input_data[field]}: {user_obj.email}")
                    setattr(user_obj, "deals", [round_def(input_data[field])])
                    logger.info(f"startup: update-info: deals updated to {input_data[field]}: {user_obj.email}")

                    if not update_into_matching(user_obj.email, {field: input_data[field]}):
                        technical_errors("STARTUP: UPDATE-INFO API DATA UPDATE UNSUCCESSFUL", user_obj.email)
                    if not update_into_matching(user_obj.email, {"deals": [round_def(input_data[field])]}):
                        technical_errors("STARTUP: UPDATE-INFO API DATA UPDATE UNSUCCESSFUL", user_obj.email)

                else:
                    setattr(user_obj, field, input_data[field])
                    logger.info(f"startup: update-info: {field} updated to {input_data[field]}: {user_obj.email}")
                    if not update_into_matching(user_obj.email, {field: input_data[field]}):
                        technical_errors("STARTUP: UPDATE-INFO API DATA UPDATE UNSUCCESSFUL", user_obj.email)

                user_obj.save()
                matching_obj = get_str_matching_data(user_obj.email)

                if matching_obj == {}:
                    technical_errors("STARTUP: NO DATA FOUND FOR USER IN MACHINE LEARNING COLLECTION", user_obj.email)

                _id = matching_obj.get("_id")

                if not reset_settings(_id):
                    technical_errors("STARTUP: WEIGHT ADJUSTMENT UPDATE UNSUCCESSFUL", user_obj.email)

            else:
                jsonify({"result": False, "error": "invalid user field"})


        ma_schema = StartupUserSchema()
        user_objs = ma_schema.dump(user_obj)

        rev_sectors_data = rev_sector_data()
        rev_progress_data = rev_progress_mapping()

        user_objs["progress"] = [rev_progress_data.get(i) for i in user_objs["progress"] if rev_progress_data.get(i)]
        user_objs["sectors"] = [rev_sectors_data.get(i) for i in user_objs["sectors"] if rev_sectors_data.get(i)]

        ret_obj = {
            "result": True,
            "user": user_objs,
        }
        return ret_obj
    else:
        jsonify({"result": False, "error": "user is not authenticated"})


#<==================================================================================================>
#                                 MONDAY NOTIFICATIONS
#<==================================================================================================>
@startup_blueprint.route('/monday-notifications', methods=["POST"])
@jwt_required
def monday_notifications():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    str_obj = jwt_decode["user_obj"]

    if request.method == "POST":
        response = validate_str_monday_notification_schema(request.get_json())
        if response["result"]:
            inp_data = response["data"]["monday_notification"]
            setattr(str_obj,"monday_notification", inp_data)
            str_obj.save()
            logger.debug(f"startup: monday-notifications: monday notification set to {inp_data}: {str_obj.email}")

            if not update_into_matching(str_obj.email, {"monday_notification": response["data"]["monday_notification"]}):
                technical_errors("STARTUP: MONDAY NOTIFICATIONS UPDATE UNSUCCESSFUL", str_obj.email)

            return jsonify({"result": True, "message": "value updated"})
        else:
            return jsonify(response)


#<==================================================================================================>
#                                  PROFILE VISIBILITY
#<==================================================================================================>
@startup_blueprint.route('/profile-visibility', methods=["POST"])
@jwt_required
def profile_visibility():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    str_obj = jwt_decode["user_obj"]

    response = validate_profile_vis_schema(request.get_json())
    if response["result"]:
        visible = response["data"]["visible"]
        setattr(str_obj, "show_profile", visible)
        str_obj.save()
        logger.debug(f"startup: profile-visibility: profile visibility set to {visible}: {str_obj.email}")

        matching_obj = get_str_matching_data(str_obj.email)

        if matching_obj == {}:
            return {"result": False, "message": "no match found"}

        _id = matching_obj.get("_id")

        if visible:
            if not unhide_user(email=str_obj.email, id=_id):
                technical_errors("STARTUP: UNHIDE PROFILE UPDATE UNSUCCESSFUL INTO HIDE PROFILE COLLECTION", str_obj.email)
        elif not visible:
            if not hide_user(email=str_obj.email, id=_id):
                technical_errors("STARTUP: HIDE PROFILE UPDATE UNSUCCESSFUL INTO HIDE PROFILE COLLECTION", str_obj.email)

            if not hide_profile_from_discover(_id):
                technical_errors("STARTUP: HIDE PROFILE UPDATE UNSUCCESSFUL INTO MACHINE LEARNING CODE", str_obj.email)

        if not update_into_matching(str_obj.email, {"show_profile": visible}):
            technical_errors("STARTUP: SHOW PROFILE UPDATE UNSUCCESSFUL INTO MACHINE LEARNING COLLECTION", str_obj.email)

        return jsonify({"result": True, "message": "value updated"})
    else:
        return jsonify(response)


#<==================================================================================================>
#                                    REMOVE SLIDE DECK
#<==================================================================================================>
@startup_blueprint.route('/remove-slide-deck', methods=["POST"])
@jwt_required
def remove_slide_deck():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    str_obj = jwt_decode["user_obj"]

    response = validate_remove_slide_deck_schema(request.get_json())
    if response["result"]:
        remove = response["data"]["remove_slide_deck"]
        if remove:
            setattr(str_obj, "slide_deck", None)
            str_obj.save()
            logger.debug(f"startup: remove-slide-deck: slide removed for user: {str_obj.email}")

        if not update_into_matching(str_obj.email, {"slide_deck": None}):
            technical_errors("STARTUP: SLIDE DECK UPDATE UNSUCCESSFUL", str_obj.email)

        return jsonify({"result": True, "message": "value updated"})
    else:
        return jsonify(response)


#<==================================================================================================>
#                          MIME FILE UPLOAD (IMAGE + APPLICATION :=> PDF)
#<==================================================================================================>
@startup_blueprint.route('/mime-files', methods=["POST"])
@jwt_required
def mime_files():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
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
        return jsonify({"result": False, "error": "missing key data"})

    file_location = f"{os.getcwd()}/{str(uuid.uuid4())}"
    if os._exists(file_location):
        shutil.rmtree(file_location)

    os.mkdir(file_location)
    with open(f"{file_location}/{file_name}", 'wb') as f:
        f.write(file_obj.read())

    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(f"{file_location}/{file_name}")
    mime_base = mime_type.split('/', 1)[0]  # base mime type :=> application (for pdf) or image (for image)
    mime_extention = mime_type.split('/', 1)[1]  # pdf or jpeg

    if file_type == "application":
        if mime_extention == "pdf":
            pdf_url = pdf_upload_to_s3(file_name, mime_extention, file_location, file_name)
            user_obj.slide_deck = pdf_url
            user_obj.save()
            shutil.rmtree(file_location)
            logger.debug(f"startup: mime-files: slide deck updated: {user_obj.email}")
            return jsonify({"result": True, "url": pdf_url})
        else:
            shutil.rmtree(file_location)
            return jsonify({"result": False, "error": "pdf file required"})

    elif file_type == "image":
        if mime_base == "image":
            image_url = profile_pic_upload_to_s3(file_name, mime_extention, file_location, file_name)
            user_obj.profile_pic_link = image_url
            user_obj.save()
            shutil.rmtree(file_location)
            logger.debug(f"startup: mime-files: profile pic updated: {user_obj.email}")
            return jsonify({"result": True, "url": image_url})
        else:
            shutil.rmtree(file_location)
            return jsonify({"result": False, "error": "image file required"})

    else:
        shutil.rmtree(file_location)
        return jsonify({"result": False, "error": "invalid file type"})


#<==================================================================================================>
#                                IMAGE UPLOAD TO S3 (CO FOUNDERS)
#<==================================================================================================>
@startup_blueprint.route('/image-upload', methods=["POST"])
@jwt_required
def co_founders_image_upload_to_s3():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
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
        return jsonify({"result": False, "error": "missing key data"})

    file_location = f"{os.getcwd()}/{str(uuid.uuid4())}"
    if os._exists(file_location):
        shutil.rmtree(file_location)

    os.mkdir(file_location)
    with open(f"{file_location}/{file_name}", 'wb') as f:
        f.write(file_obj.read())

    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(f"{file_location}/{file_name}")
    mime_base = mime_type.split('/',1)[0]        # base mime type
    mime_extention = mime_type.split('/', 1)[1]  # jpeg

    if file_type == "image":
        if mime_base == "image":
            image_url = profile_pic_upload_to_s3(file_name, mime_extention, file_location, file_name)
            shutil.rmtree(file_location)
            logger.debug(f"startup: image-upload: profile pic updated: {user_obj.email}")
            return jsonify({"result": True, "url": image_url})
        else:
            shutil.rmtree(file_location)
            return jsonify({"result": False, "error": "image file required"})

    else:
        shutil.rmtree(file_location)
        return jsonify({"result": False, "error": "invalid file type"})


#<==================================================================================================>
#                                     WAIT LIST API
#<==================================================================================================>
@startup_blueprint.route('/waitlist', methods=['GET'])
@jwt_required
def waitlist_email():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    user_obj = jwt_decode["user_obj"]

    email, first_name, company_name = user_obj.email, user_obj.first_name, user_obj.company_name
    if email:
        email = email.lower()
    thread = threading.Thread(target=wait_list_user_str, args=(email, first_name, company_name))
    thread.start()
    return jsonify({"result": True, "message": "email sent if the user exists"})


#<==================================================================================================>
#                                          DASHBOARD
#<==================================================================================================>
@startup_blueprint.route('/dashboard', methods=["GET", "POST"])
@jwt_required
def startup_dashboard():
    if request.method == "GET":
        jwt_decode = startup_jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        user_obj = jwt_decode["user_obj"]
        matching_obj = get_str_matching_data(user_obj.email)

        if matching_obj == {}:
            return {"result": False, "message": "no match found"}

        _id = matching_obj.get("_id")
        if not _id:
            return {"result": False, "message": "no id found"}

        discover = get_discover(_id)

        if not discover["result"]:
            logger.debug(f"startup: dashboard: no match found: {user_obj.email}")
            return {"result": False, "message": "no match found"}

        elif discover["result"] and discover["data"] == []:
            logger.debug(f"startup: dashboard: no match found: {user_obj.email}")
            return {"result": False, "message": "no match found"}

        else:
            logger.debug(f"startup: dashboard: data found: {user_obj.email}")
            str_data = process_all_str_data(discover["data"])
            return jsonify({"result": True, "data": str_data})

    elif request.method == "POST":
        jwt_decode = startup_jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        str_obj = jwt_decode["user_obj"]

        str_email = str_obj.email

        response = validate_dashboard_schema(request.get_json())
        if not response["result"]:
            return jsonify(response)

        user_id = response["data"]["user_id"]

        inv_obj = Investor.objects.filter(id=user_id).first()
        if not inv_obj:
            return jsonify({"result": False, "error": "user does not exist"})

        inv_email = inv_obj.email
        inv_invite = response["data"]["invite"]

        if str_obj.connected.get(inv_email):
            logger.debug(f"startup: dashboard: already connected: {str_email} to {inv_obj}: {str_obj.email}")
            return jsonify({"result": False, "message": "already connected"})

        if str_obj.passed.get(inv_email):
            if inv_email in getattr(str_obj, "pending"):
                pending_obj = dict(str_obj.pending)
                pending_obj.pop(inv_email)
                str_obj.pending = pending_obj
                str_obj.save()

                inv_transactional_replicas = inv_mutual_updates(inv_obj)
                str_transactional_replicas = str_mutual_updates(str_obj)

                if not inv_transactional_replicas:
                    logger.debug(f"startup: dashboard: dashboard update unsuccessful: {inv_obj.email}")
                    technical_errors("INVESTOR: DASHBOARD UPDATE UNSUCCESSFUL", inv_obj.email)

                if not str_transactional_replicas:
                    logger.debug(f"startup: dashboard: dashboard update unsuccessful: {str_obj.email}")
                    technical_errors("STARTUP: DASHBOARD UPDATE UNSUCCESSFUL", str_obj.email)

                str_matching_obj = get_str_matching_data(str_email)
                str_id = str_matching_obj.get("_id")

                inv_matching_obj = get_inv_matching_data(inv_email)
                inv_id = inv_matching_obj.get("_id")

                resp = set_response(str_id, inv_id, True)
                if not resp.get("result"):
                    logger.debug(f"startup: dashboard: set response unsuccessful from: {str_id} to {inv_id}: True: {str_obj.email}")
                    technical_errors("STARTUP: SET RESPONSE UNSUCCESSFUL", str_obj.email)
                else:
                    logger.debug(f"startup: dashboard: set response successful from: {str_id} to {inv_id}: True: {str_obj.email}")

            return jsonify({"result": False, "message": "already passed"})

        if not inv_invite:
            str_passed_requests = dict(str_obj.passed)
            str_passed_requests[inv_email] = True
            str_obj.passed = str_passed_requests

            str_obj.save()

            inv_transactional_replicas = inv_mutual_updates(inv_obj)
            str_transactional_replicas = str_mutual_updates(str_obj)

            if not inv_transactional_replicas:
                logger.debug(f"startup: dashboard: dashboard update unsuccessful: {inv_obj.email}")
                technical_errors("INVESTOR: DASHBOARD UPDATE UNSUCCESSFUL", inv_obj.email)

            if not str_transactional_replicas:
                logger.debug(f"startup: dashboard: dashboard update unsuccessful: {str_obj.email}")
                technical_errors("STARTUP: DASHBOARD UPDATE UNSUCCESSFUL", str_obj.email)

            str_matching_obj = get_str_matching_data(str_email)
            str_id = str_matching_obj.get("_id")

            inv_matching_obj = get_inv_matching_data(inv_email)
            inv_id = inv_matching_obj.get("_id")

            resp = set_response(str_id, inv_id, False)
            if not resp.get("result"):
                logger.debug(f"startup: dashboard: set response unsuccessful from: {str_id} to {inv_id}: False: {str_obj.email}")
                technical_errors("STARTUP: SET RESPONSE UNSUCCESSFUL", str_obj.email)
            else:
                logger.debug(f"startup: dashboard: set response successful from: {str_id} to {inv_id}: False: {inv_obj.email}")

            return jsonify({"result": True, "message": "passed"})

        if inv_invite:
            def all_info():
                temp_dict = {}
                temp_dict["inv_fn"] = inv_obj.first_name
                temp_dict["str_fn"] = str_obj.first_name
                temp_dict["str_cn"] = str_obj.company_name
                temp_dict["str_seeking"] = str_obj.round_size
                temp_dict["str_pitch"] = str_obj.startup_pitch
                temp_dict["str_founders"] = str_obj.co_founders[0].get("name")
                return temp_dict

            inv_pending_requests = dict(inv_obj.pending)
            inv_connected_requests = dict(inv_obj.connected)
            inv_obj = Investor.objects.filter(email=inv_email).first()

            if inv_pending_requests.get(str_email):

                str_pending_requests = dict(str_obj.pending)
                if str_pending_requests.get(inv_email):
                    str_pending_requests.pop(inv_email)
                str_obj.pending = str_pending_requests

                str_passed_requests = dict(str_obj.passed)
                if str_passed_requests.get(inv_email):
                    str_passed_requests.pop(inv_email)
                str_obj.passed = str_passed_requests

                inv_pending_requests = dict(inv_obj.pending)
                if inv_pending_requests.get(str_email):
                    inv_pending_requests.pop(str_email)
                inv_obj.pending = inv_pending_requests

                inv_passed_requests = dict(inv_obj.passed)
                if inv_passed_requests.get(str_email):
                    inv_passed_requests.pop(str_email)
                inv_obj.passed = inv_passed_requests

                inv_connected_requests = dict(inv_obj.connected)
                inv_connected_requests[str_email] = True
                inv_obj.connected = inv_connected_requests

                str_connected_requests = dict(str_obj.connected)
                str_connected_requests[inv_email] = True
                str_obj.connected = str_connected_requests

                inv_obj.save()
                str_obj.save()

                inv_transactional_replicas = inv_mutual_updates(inv_obj)
                str_transactional_replicas = str_mutual_updates(str_obj)

                if not inv_transactional_replicas:
                    technical_errors("INVESTOR: DASHBOARD UPDATE UNSUCCESSFUL", inv_obj.email)

                if not str_transactional_replicas:
                    technical_errors("STARTUP: DASHBOARD UPDATE UNSUCCESSFUL", str_obj.email)

                email_connected(inv_email, str_email, all_info())

                str_matching_obj = get_str_matching_data(str_email)
                str_id = str_matching_obj.get("_id")

                inv_matching_obj = get_inv_matching_data(inv_email)
                inv_id = inv_matching_obj.get("_id")

                resp = set_response(str_id, inv_id, True)
                if not resp.get("result"):
                    logger.debug(f"startup: dashboard: set response unsuccessful from: {str_id} to {inv_id}: True: {str_obj.email}")
                    technical_errors("STARTUP: SET RESPONSE UNSUCCESSFUL", str_obj.email)
                else:
                    logger.debug(f"startup: dashboard: set response successful from: {str_id} to {inv_id}: True: {str_obj.email}")

                return jsonify({"result": True, "message": "connected"})

            elif inv_connected_requests.get(inv_email):
                str_pending_requests = dict(str_obj.pending)
                if str_pending_requests.get(inv_email):
                    str_pending_requests.pop(inv_email)
                str_obj.pending = str_pending_requests

                inv_pending_requests = dict(inv_obj.pending)
                if inv_pending_requests.get(str_email):
                    inv_pending_requests.pop(str_email)
                inv_obj.pending = inv_pending_requests

                str_connected_requests = dict(str_obj.connected)
                str_connected_requests[inv_email] = True
                str_obj.connected = str_connected_requests

                inv_obj.save()
                str_obj.save()

                inv_transactional_replicas = inv_mutual_updates(inv_obj)
                str_transactional_replicas = str_mutual_updates(str_obj)

                if not inv_transactional_replicas:
                    logger.debug(f"startup: dashboard: dashboard update unsuccessful: {inv_obj.email}")
                    technical_errors("INVESTOR: DASHBOARD UPDATE UNSUCCESSFUL", inv_obj.email)

                if not str_transactional_replicas:
                    logger.debug(f"startup: dashboard: dashboard update unsuccessful: {str_obj.email}")
                    technical_errors("STARTUP: DASHBOARD UPDATE UNSUCCESSFUL", str_obj.email)

                str_matching_obj = get_str_matching_data(str_email)
                str_id = str_matching_obj.get("_id")

                inv_matching_obj = get_inv_matching_data(inv_email)
                inv_id = inv_matching_obj.get("_id")

                resp = set_response(str_id, inv_id, True)
                if not resp.get("result"):
                    logger.debug(f"startup: dashboard: set response unsuccessful from: {str_id} to {inv_id}: True: {str_obj.email}")
                    technical_errors("STARTUP: SET RESPONSE UNSUCCESSFUL", str_obj.email)
                else:
                    logger.debug(f"startup: dashboard: set response successful from: {str_id} to {inv_id}: True: {str_obj.email}")

                email_connected(inv_email, str_email, all_info())

                return jsonify({"result": True, "message": "connected"})
            else:
                str_passed_requests = dict(str_obj.passed)
                if str_passed_requests.get(inv_email):
                    str_passed_requests.pop(inv_email)
                str_obj.passed = str_passed_requests

                str_connected_requests = dict(str_obj.connected)
                if str_connected_requests.get(inv_email):
                    str_connected_requests.pop(inv_email)
                str_obj.connected = str_connected_requests

                str_pending_req = dict(str_obj.pending)
                str_pending_req[inv_email] = True
                str_obj.pending = str_pending_req

                str_obj.save()

                inv_transactional_replicas = inv_mutual_updates(inv_obj)
                str_transactional_replicas = str_mutual_updates(str_obj)

                if not inv_transactional_replicas:
                    logger.debug(f"startup: dashboard: dashboard update unsuccessful: {inv_obj.email}")
                    technical_errors("INVESTOR: DASHBOARD UPDATE UNSUCCESSFUL", inv_obj.email)

                if not str_transactional_replicas:
                    logger.debug(f"startup: dashboard: dashboard update unsuccessful: {str_obj.email}")
                    technical_errors("STARTUP: DASHBOARD UPDATE UNSUCCESSFUL", str_obj.email)

                str_matching_obj = get_str_matching_data(str_email)
                str_id = str_matching_obj.get("_id")

                inv_matching_obj = get_inv_matching_data(inv_email)
                inv_id = inv_matching_obj.get("_id")

                resp = set_response(str_id, inv_id, True)
                if not resp.get("result"):
                    logger.debug(f"startup: dashboard: set response unsuccessful from: {str_id} to {inv_id}: True: {str_obj.email}")
                    technical_errors("STARTUP: SET RESPONSE UNSUCCESSFUL", str_obj.email)
                else:
                    logger.debug(f"startup: dashboard: set response successful from: {str_id} to {inv_id}: True: {str_obj.email}")

                return jsonify({"result": True, "message": "invitation"})


#<==================================================================================================>
#                                       HISTORY ALL
#<==================================================================================================>
@startup_blueprint.route('/history-all', methods=["GET"])
@jwt_required
def history():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    data = []
    str_obj = jwt_decode["user_obj"]

    # # passed
    feedback = getattr(str_obj, "feedback")
    feedback_schema = InvestorFeedbackSchema()
    for k, v in feedback.items():
        if not v.get("is_anonymous"):
            inv_obj = Investor.objects.filter(email=k).first()
            resp = feedback_schema.dump(inv_obj)
            resp["comment"] = v.get("comment")
            resp["reason"] = v.get("fields")[0].capitalize() if v.get("fields") else None
            data.append(resp)
        else:
            resp = {}
            resp["deals"] = []
            resp["location"] = None
            resp["last_name"] = None
            resp["action"] = "Passed"
            resp["first_name"] = None
            resp["first_name"] = None
            resp["comment"] = v.get("comment")
            resp["profile_pic_link"] = CONSTANT.ANONYMOUS_PP.value
            resp["reason"] = v.get("fields")[0].capitalize() if v.get("fields") else None
            data.append(resp)

    # connected
    connected = getattr(str_obj, "connected")
    ma_schema = InvestorConnectedSchema()
    for k, v in connected.items():
        inv_obj = Investor.objects.filter(email=k).first()
        temp_resp = ma_schema.dump(inv_obj)
        data.append(temp_resp)

    logger.debug(f"startup: history-all: data found: {str_obj.email}")
    return jsonify({"result": True, "data": data})


#<==================================================================================================>
#                                      HISTORY CONNECTED
#<==================================================================================================>
@startup_blueprint.route('/history-connected', methods=["GET"])
@jwt_required
def connected():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    str_obj = jwt_decode["user_obj"]

    connected = getattr(str_obj, "connected")
    ma_schema = InvestorConnectedSchema()

    data = []
    for k,v in connected.items():
        inv_obj = Investor.objects.filter(email=k).first()
        temp_obj = ma_schema.dump(inv_obj)
        data.append(temp_obj)

    logger.debug(f"startup: history-connected: data found: {str_obj.email}")
    return jsonify({"result": True, "data": data})



#<==================================================================================================>
#                                    HISTORY PASSED
#<==================================================================================================>
@startup_blueprint.route('/history-passed', methods=["GET"])
@jwt_required
def passed():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    data = []
    str_obj = jwt_decode["user_obj"]

    feedback = getattr(str_obj, "feedback")
    feedback_schema = InvestorFeedbackSchema()

    for k, v in feedback.items():
        if not v.get("is_anonymous"):
            inv_obj = Investor.objects.filter(email=k).first()
            resp = feedback_schema.dump(inv_obj)
            resp["comment"] = v.get("comment")
            resp["reason"] = v.get("fields")[0].capitalize() if v.get("fields") else None
            data.append(resp)
        else:
            resp = {}
            resp["deals"] = []
            resp["location"] = None
            resp["last_name"] = None
            resp["action"] = "Passed"
            resp["first_name"] = None
            resp["first_name"] = None
            resp["comment"] = v.get("comment")
            resp["profile_pic_link"] = CONSTANT.ANONYMOUS_PP.value
            resp["reason"] = v.get("fields")[0].capitalize() if v.get("fields") else None
            data.append(resp)

    logger.debug(f"startup: history-passed: data found: {str_obj.email}")
    return {"result": True, "data": data}


#<==================================================================================================>
#                                 HISTORY CONNECTED REVISIT
#<==================================================================================================>
@startup_blueprint.route('/history-connected-profile-view', methods=["POST"])
@jwt_required
def passed_revisit():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    str_obj = jwt_decode["user_obj"]
    input_req = request.get_json()
    response = validate_inv_passed_recvisit_schema(input_req)

    if response["result"]:
        user_id = response["data"]["user_id"]
        inv_obj = Investor.objects.filter(id=user_id).first()
        if not inv_obj:
            return jsonify({"result": False, "error": "user does not exist"})

        ma_schema = InvestorDashboardSchema()
        data = ma_schema.dump(inv_obj)
        logger.debug(f"startup: history-connected-profile-view: data found: {str_obj.email}")
        return jsonify({"result": True, "data": data})
    else:
        return jsonify(response)


#<==================================================================================================>
#                                    VERIFY PASSOWRD :=> DELETE ACCOUNT
#<==================================================================================================>
@startup_blueprint.route('/verify-password', methods=["POST"])
@jwt_required
def verify_password():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    str_obj = jwt_decode["user_obj"]
    response = validate_delete_acc_schema(request.get_json())
    if response["result"]:
        password = response["data"]["password"]
        if check_password_hash(str_obj.password, password):
            logger.debug(f"startup: verify-password: correct password: {str_obj.email}")
            return jsonify({"result": True, "message": "correct credentials"})
        logger.debug(f"startup: verify-password: wrong password: {str_obj.email}")
        return jsonify({"result": False, "message": "wrong credentials"})
    return jsonify(response)


#<==================================================================================================>
#                                    FINAL DELETE :=> DELETE ACCOUNT
#<==================================================================================================>
@startup_blueprint.route('/delete-account', methods=["POST"])
@jwt_required
def delete_account():
    if request.method == "POST":
        jwt_decode = startup_jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        str_obj = jwt_decode["user_obj"]

        response = validate_delete_acc_conf_schema(request.get_json())
        if response["result"]:
            delete = response["data"]["delete"]
            if delete:
                setattr(str_obj, "delete_account", delete)
                str_obj.save()
                logger.debug(f"startup: delete-account: account deleted: {str_obj.email}")

                matching_obj = get_str_matching_data(str_obj.email)
                str_id = matching_obj.get("_id")
                if not delete_user_ml(str_id):
                    technical_errors("STARTUP: DELETE ACCOUNT UPDATE UNSUCCESSFUL", str_obj.email)

                thread = threading.Thread(target=delete_user_account, args=(str_obj.email, ))
                thread.start()

                return jsonify({"result": True, "message": "account deleted"})
            return jsonify({"result": False, "message": "account not deleted"})
        return jsonify(response)



#<==================================================================================================>
#                               PASSWORD RESET REQUEST (HOMEPAGE)
#<==================================================================================================>
@startup_blueprint.route('/forgot-password', methods=['POST'])
def forgot_password():
    input_request = request.get_json()
    response = validate_email_schema(input_request)
    if response["result"]:
        email = response["data"]["email"]
        if email:
            email = email.lower()
        user = Startup.objects.filter(email=email).first()

        if user is None:
            logger.debug(f"startup: forgot-password: user does not exist : {email}")
            return jsonify({"result": True, "message": "email sent if the user exists"})

        token = serial.dumps(user.email, salt='email_reset')
        link = url_for('startup.reset_link', token=token, _external=True)
        user.password_reset_meta_data = {"is_clicked": False}
        user.save()
        logger.debug(f"startup: forgot-password: forgot password link generated: {email}")

        thread = threading.Thread(target=password_reset_email, args=(email, link,))
        thread.start()
        return jsonify({"result": True, "message": "email sent if the user exists"})
    else:
        return jsonify(response)


#<==================================================================================================>
#                               CHANGE PASSWORD (PROFILE SETTINGS)
#<==================================================================================================>
@startup_blueprint.route('/change-password', methods=["GET"])
@jwt_required
def change_password():
    jwt_decode = startup_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    str_obj = jwt_decode["user_obj"]

    if str_obj is not None:
        token = serial.dumps(str_obj.email, salt='email_reset')
        link = url_for('startup.reset_link', token=token, _external=True)
        str_obj.password_reset_meta_data = {"is_clicked": False}
        str_obj.save()
        logger.debug(f"startup: change-password: password link generated: {str_obj.email}")

        thread = threading.Thread(target=password_reset_email, args=(str_obj.email, link,))
        thread.start()
        return jsonify({"result": True, "message": "email sent if the user exists"})
    else:
        return jsonify({"result": False, "error": "user does not exists"})


#<==================================================================================================>
#                                  GET JWT TOKEN FOR CONFIRMATION PAGE
#<==================================================================================================>
@startup_blueprint.route('/get-jwt-token', methods=['POST'])
def jwt_for_confirmation_page():
    input_request = request.get_json()
    response = validate_email_schema(input_request)
    if response["result"]:
        email = response["data"]["email"]
        if email:
            email = email.lower()

        user = Startup.objects.filter(email=email).first()
        if user is None:
            error = "user does not exist"
            logger.debug(f"startup: get-jwt-token: {error}: {email}")
            return jsonify({"result": False, "error": error})

        jwt_obj = {"email": email, "model": "Startup"}
        access_token = create_access_token(identity=jwt_obj)
        ret_obj = {
            "result": True,
            "token": access_token
        }
        logger.debug(f"startup: get-jwt-token: new jwt token generated: {email}")
        return jsonify(ret_obj)
    else:
        return jsonify(response)


#<==================================================================================================>
#                                       DELETE EMAIL ADDRESSES
#<==================================================================================================>
@startup_blueprint.route('/ste-mapping', methods=['POST'])
def string_to_email_mapping():
    input_req = request.get_json()
    response = validate_inv_passed_recvisit_schema(input_req)

    if response["result"]:
        user_id = response["data"]["user_id"]
        str_obj = Investor.objects.filter(id=user_id).first()
        if not str_obj:
            return jsonify({"result": False, "error": "user does not exist"})
        else:
            email = str_obj.email
            return jsonify({"result": True, "email": email})
    return response