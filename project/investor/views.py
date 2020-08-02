#<==================================================================================================>
#                                       IMPORTS
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
from flask_login import login_required, login_user
from common_utilities.referral_email import email_referral
from common_utilities.jwt_decoder import investor_jwt_decoder
from common_utilities.connected_emails import email_connected
from common_utilities.company_images import company_images_api
from common_utilities.password_reset import password_reset_email
from common_utilities.email_confirmation import email_confirmation
from common_utilities.technical_error_mail import technical_errors
from project.models import Investor, Startup, Referrals, AngelGroup
from common_utilities.google_email import google_email_confirmation
from common_utilities.wait_list_email_inv import wait_list_user_inv
from common_utilities.account_delete_email import delete_user_account
from common_utilities.hide_user_profile import hide_user, unhide_user
from common_utilities.mime_files_upload import profile_pic_upload_to_s3
from werkzeug.security import generate_password_hash, check_password_hash
from common_utilities.common_mappings import sector_data, accreditation_data
from project.investor.marshmallow_serialize import InvestorUserSchema, InvestorMLSchema
from flask import url_for, request, Blueprint, jsonify, redirect, session, render_template
from common_utilities.startup_matching_db import get_str_matching_data, str_mutual_updates
from common_utilities.reverse_common_mapping import rev_accreditation_data, rev_sector_data
from common_utilities.flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from common_utilities.unique_login import inv_unique_users_daily, inv_unique_users_monthly, inv_unique_users_weekly
from project.startup.marshmallow_serialize import StartupConnectedSchema, StartupPassedSchema, StartupDashboardSchema
from common_utilities.ml_apis import get_discover, set_response, delete_user_ml, reset_settings, hide_profile_from_discover
from common_utilities.new_user_count_analytics import inv_daily_new_users_count, inv_weekly_new_users_count, inv_monthly_new_users_count
from common_utilities.investor_matching_db import (insert_into_matching, update_into_matching, get_inv_matching_data, process_all_str_data,
                                                   inv_mutual_updates)
from common_utilities.json_schema_investor_validation import (validate_inv_first_page_schema, validate_email_schema, validate_dashboard_schema,
                                                              validate_referrer_schema, validate_company_schema, validate_inv_passed_recvisit_schema,
                                                              validate_google_schema, validate_inv_login_schema, validate_delete_acc_schema,
                                                              validate_inv_monday_notification_schema, validate_profile_vis_schema,
                                                              validate_inv_angel_group_name_schema, validate_delete_acc_conf_schema)


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

                    if email:
                        email = email.lower()

                    user = Investor.objects.filter(email=email).first()
                    if user:
                        if getattr(user, "delete_account"):
                            return jsonify({"result": False, "error": "account deleted"})

                        login_user(user)
                        user.is_logged_in = True
                        user.save()
                        logger.debug(f"investor logged in: {email}")

                        unique_user_list = [inv_unique_users_daily, inv_unique_users_weekly, inv_unique_users_monthly]
                        for i in unique_user_list:
                            unique_user_thread = threading.Thread(target=i, args=(email,))
                            unique_user_thread.start()

                        ma_schema = InvestorUserSchema()
                        user_objs = ma_schema.dump(user)

                        rev_acc_data = rev_accreditation_data()
                        rev_sectors_data = rev_sector_data()

                        user_objs["accreditation"] = rev_acc_data.get(user_objs["accreditation"])
                        user_objs["sectors"] = [rev_sectors_data.get(i) for i in user_objs["sectors"] if rev_sectors_data.get(i)]

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

                        ml_schema = InvestorMLSchema()
                        user = Investor.objects.filter(email=email).first()
                        ml_schema_resp = ml_schema.dump(user)
                        if not insert_into_matching(email, ml_schema_resp):
                            technical_errors("INVESTOR: SIGNUP FLOW UPDATE UNSUCCESSFUL", email)

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

                        user_count_analytics = [inv_daily_new_users_count, inv_weekly_new_users_count, inv_monthly_new_users_count]
                        for i in user_count_analytics:
                            login_cnt_thread = threading.Thread(target=i, args=())
                            login_cnt_thread.start()

                        rev_acc_data = rev_accreditation_data()
                        rev_sectors_data = rev_sector_data()

                        user_objs["accreditation"] = rev_acc_data.get(user_objs["accreditation"])
                        user_objs["sectors"] = [rev_sectors_data.get(i) for i in user_objs["sectors"] if rev_sectors_data.get(i)]

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
                    return jsonify({"result": False, "error": message}), 400
            else:
                return jsonify({"result": False, "error": "invalid token"}), 400
        except:
            return jsonify({"result": False, "error": "token not validated"}), 400
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

        if email:
            email = email.lower()

        user = Investor.objects.filter(email=email).first()
        if user is None:
            error = "user does not exist"
            logger.debug(f"investor does not exixt: {email}")
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

            unique_user_list = [inv_unique_users_daily, inv_unique_users_weekly, inv_unique_users_monthly]
            for i in unique_user_list:
                unique_user_thread = threading.Thread(target=i, args=(email,))
                unique_user_thread.start()

            ma_schema = InvestorUserSchema()
            user_objs = ma_schema.dump(user)

            rev_acc_data = rev_accreditation_data()
            rev_sectors_data = rev_sector_data()

            user_objs["accreditation"] = rev_acc_data.get(user_objs["accreditation"])
            user_objs["sectors"] = [ rev_sectors_data.get(i) for i in user_objs["sectors"] if rev_sectors_data.get(i)]

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
            error = "wrong credentials"
            return jsonify({"result": False, "error": error})
    else:
        return jsonify(response)


#<==================================================================================================>
#                                      PASSWORD RESET LINK
#<==================================================================================================>
@investor_blueprint.route('/reset-link/<token>', methods=['GET', 'POST'])
def reset_link(token):
    if request.method == "GET":
        try:
            email = serial.loads(token, salt='email_reset', max_age=int(CONSTANT.PASSWORD_RESET_LINK_AGE.value))
            if email:
                email = email.lower()
        except:
            return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)

        user = Investor.objects.filter(email=email).first()
        if user:
            if user.password_reset_meta_data == {}:
                return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)
        return render_template("reset.html")

    elif request.method == "POST":
        try:
            email = serial.loads(token, salt='email_reset', max_age=int(CONSTANT.PASSWORD_RESET_LINK_AGE.value))
            if email:
                email = email.lower()
        except:
            return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)

        user = Investor.objects.filter(email=email).first()
        if user:
            password = request.form.get("password")

            if user.password_reset_meta_data == {}:
                return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)

            if not user.password_reset_meta_data["is_clicked"]:
                user.password = generate_password_hash(password)
                user.password_reset_meta_data = {}
                user.save()
                logger.debug(f"investor password changed: {email}")
                return render_template("reset-success-inv.html")
        else:
            return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)


#<==================================================================================================>
#                               PASSWORD RESET REQUEST (HOMEPAGE)
#<==================================================================================================>
@investor_blueprint.route('/forgot-password', methods=['POST'])
def forgot_password():
    input_request = request.get_json()
    response = validate_email_schema(input_request)
    if response["result"]:
        email = response["data"]["email"]
        if email:
            email = email.lower()
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
        if email:
            email = email.lower()

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
            technical_errors("INVESTOR: REGISTER UPDATE UNSUCCESSFUL", email)

        logger.debug(f"investor created {email}")

        token = serial.dumps(email, salt='email_confirm')
        link = url_for('investor.email_confirmed', token=token, _external=True)
        thread = threading.Thread(target=email_confirmation, args=(email, link, input_request.get("first_name")))
        thread.start()

        user_count_analytics = [inv_daily_new_users_count, inv_weekly_new_users_count, inv_monthly_new_users_count]
        for i in user_count_analytics:
            login_cnt_thread = threading.Thread(target=i, args=())
            login_cnt_thread.start()

        user.passowrd_confirm_meta_data = {"is_clicked": False}
        user.save()

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
        if email:
            email = email.lower()
    except:
        return redirect(f"{CONSTANT.CURRENT_SERVER.value}/login", code=302)

    user = Investor.objects.filter(email=email).first()

    if user:
        if user.passowrd_confirm_meta_data == {}:
            return redirect(f"{CONSTANT.CURRENT_SERVER.value}/login", code=302)
        else:
            user.email_confirmed = True
            user.save()

        if not update_into_matching(email, {"email_confirmed": True}):
            technical_errors("INVESTOR: EMAIL CONFIRMATION UPDATE UNSUCCESSFUL", email)

        logger.debug(f"investor email confirmed {email}")

        login_user(user)
        user.is_logged_in = True
        user.passowrd_confirm_meta_data = {}
        user.save()
        session["email"] = email
        logger.debug(f"investor logged in: {email}")
        return redirect(url_for("investor.confirmation_signup_flow", email=email, code=302))

    else:
        logger.debug(f"investor does not exist {email}")
        return redirect(f"{CONSTANT.CURRENT_SERVER.value}/investor/signup")


#<==================================================================================================>
#                                   CONFIRMATION SIGNUP FLOW
#<==================================================================================================>
@investor_blueprint.route('/confirmation-signup-flow', methods=["GET"])
@login_required
def confirmation_signup_flow():
    email = session.get("email")

    if email:
        email = email.lower()

    if not email:
        return jsonify({"reuslt": False, "error": "session expired"})

    inv_obj = Investor.objects.filter(email=email).first()
    first_name = (inv_obj.first_name).strip().replace(" ", "_")
    last_name = (inv_obj.last_name).strip().replace(" ", "_")
    query_string = f"confirmed=True&email={inv_obj.email}&fn={first_name}&ln={last_name}&investor=true"
    return redirect(f"{CONSTANT.CURRENT_SERVER.value}/investor/signup?{query_string}"), 302


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

    if ref_email:
        ref_email = ref_email.lower()

    if Investor.objects.filter(email=ref_email).first():
        return jsonify({"result": False, "error": "user exists"})

    if Startup.objects.filter(email=ref_email).first():
        return jsonify({"result": False, "error": "user exists"})

    full_name = user_obj.first_name + " " + user_obj.last_name
    first_name = user_obj.first_name

    ref_obj = {"referred_by": user_obj.email, "referred": ref_email}

    token = serial.dumps(ref_obj, salt='email_referral')
    link = url_for('investor.referral_verification', token=token, _external=True)
    thread = threading.Thread(target=email_referral,
                              args=((ref_email, full_name, first_name, link, "investor",
                                     CONSTANT.CURRENT_SERVER.value)))
    thread.start()

    return jsonify({"result": True, "message": "mail sent"})


#<==================================================================================================>
#                                  REFERRAL VERIFICATION
#<==================================================================================================>
@investor_blueprint.route('/referral/<token>', methods=["GET"])
def referral_verification(token):
    try:
        ref_obj = serial.loads(token, salt='email_referral')
        referred_by = ref_obj.get("referred_by")
        referred = ref_obj.get("referred")
    except:
        return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)

    user = Investor.objects.filter(email=referred_by).first()

    if user:
        # For referred_by user
        ref_by_obj = Referrals.objects.filter(email=user.email).first()
        if ref_by_obj:
            details = dict(ref_by_obj.details)
            referred_to = list(details.get("referred_to"))
            if referred in referred_to:
                logger.debug(f"{referred} is already referred by {referred_by}")
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
            logger.debug(f"{referred} is already referred by {referred_by}")
            return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)

        details = {
            "referred_by": referred_by,
            "referred_to": []
            }
        new_ref_obj = Referrals(email=referred, details=details)
        new_ref_obj.save()

        logger.debug(f"{referred} is referred by {referred_by}")
        return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)
    else:
        logger.debug(f"investor does not exist {referred_by} :=> referral verification")
        return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)


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
        available_fields = {"sectors", "deals", "bio", "location", "prior_investments", "first_invite",
                            "accreditation", "syndicate", "angel", "profile_pic_link", "first_dashboard_visit"}

        for key in list(input_data.keys()):
            if key not in available_fields:
                return jsonify({"result": False, "error": "invalid user field"})

        for field in input_data:
            if field in available_fields:
                if field == "sectors":
                    sectors_map = sector_data()
                    res = [ sectors_map.get(i) for i in input_data[field] if sectors_map.get(i) != None ]
                    setattr(user_obj, field, res)

                    if not update_into_matching(user_obj.email, {field: res}):
                        technical_errors("INVESTOR: SIGNUP FLOW SECTORS UPDATE UNSUCCESSFUL", user_obj.email)

                elif field == "accreditation":
                    accreditation_map = accreditation_data()
                    res = accreditation_map.get(input_data[field])
                    setattr(user_obj, field, res)

                    if not update_into_matching(user_obj.email, {field: res}):
                        technical_errors("INVESTOR: SIGNUP FLOW ACCREDATIONS UPDATE UNSUCCESSFUL", user_obj.email)

                else:
                    setattr(user_obj, field, input_data[field])
                    if not update_into_matching(user_obj.email, {field: input_data[field]}):
                        technical_errors("INVESTOR: SIGNUP FLOW UPDATE UNSUCCESSFUL", user_obj.email)

                matching_obj = get_inv_matching_data(user_obj.email)

                if matching_obj == {}:
                    technical_errors("INVESTOR: NO DATA FOUND FOR USER IN MACHINE LEARNING COLLECTION", user_obj.email)

                _id = matching_obj.get("_id")
                if not reset_settings(_id):
                    technical_errors("INVESTOR: WEIGHT ADJUSTMENT UPDATE UNSUCCESSFUL", user_obj.email)
                user_obj.save()

            else:
                return jsonify({"result": False, "error": "invalid user field"})

        ma_schema = InvestorUserSchema()
        user_objs = ma_schema.dump(user_obj)

        rev_acc_data = rev_accreditation_data()
        rev_sectors_data = rev_sector_data()

        user_objs["accreditation"] = rev_acc_data.get(user_objs["accreditation"])
        user_objs["sectors"] = [rev_sectors_data.get(i) for i in user_objs["sectors"] if rev_sectors_data.get(i)]

        ret_obj = {
            "result": True,
            "user": user_objs,
        }
        return ret_obj
    else:
        return jsonify({"result": False, "error": "user is not authenticated"})


#<==================================================================================================>
#                                    MONDAY NOTIFICATION
#<==================================================================================================>
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
            setattr(inv_obj, "monday_notification", response["data"]["monday_notification"])
            inv_obj.save()

            if not update_into_matching(inv_obj.email, {"monday_notification": response["data"]["monday_notification"]}):
                technical_errors("INVESTOR: MONDAY NOTIFICATIONS UPDATE UNSUCCESSFUL", inv_obj.email)

            return jsonify({"result": True, "message": "value updated"})
        else:
            return jsonify(response)


#<==================================================================================================>
#                                    PROFILE VISIBILITY
#<==================================================================================================>
@investor_blueprint.route('/profile-visibility', methods=["POST"])
@jwt_required
def profile_visibility():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    inv_obj = jwt_decode["user_obj"]
    response = validate_profile_vis_schema(request.get_json())
    if response["result"]:
        visible = response["data"]["visible"]
        setattr(inv_obj, "show_profile", visible)
        inv_obj.save()

        matching_obj = get_inv_matching_data(inv_obj.email)

        if matching_obj == {}:
            technical_errors("INVESTOR: SHOW PROFILE UPDATE UNSUCCESSFUL INTO MACHINE LEARNING CODE", inv_obj.email)
            return {"result": False, "message": "no match found"}

        _id = matching_obj.get("_id")

        if visible:
            if not unhide_user(email=inv_obj.email, id=_id):
                technical_errors("INVESTOR: UNHIDE PROFILE UPDATE UNSUCCESSFUL INTO HIDE PROFILE COLLECTION", inv_obj.email)
        elif not visible:
            if not hide_user(email=inv_obj.email, id=_id):
                technical_errors("INVESTOR: HIDE PROFILE UPDATE UNSUCCESSFUL INTO HIDE PROFILE COLLECTION", inv_obj.email)

            if not hide_profile_from_discover(_id):
                technical_errors("INVESTOR: HIDE PROFILE UPDATE UNSUCCESSFUL INTO MACHINE LEARNING CODE", inv_obj.email)

        if not update_into_matching(inv_obj.email, {"show_profile": visible}):
            technical_errors("INVESTOR: SHOW PROFILE UPDATE UNSUCCESSFUL INTO MACHINE LEARNING COLLECTION", inv_obj.email)

        return jsonify({"result": True, "message": "value updated"})
    else:
        return jsonify(response)


#<==================================================================================================>
#                                     WAIT LIST API
#<==================================================================================================>
@investor_blueprint.route('/waitlist', methods=['GET'])
@jwt_required
def waitlist_email():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    user_obj = jwt_decode["user_obj"]
    email, first_name = user_obj.email, user_obj.first_name
    if email:
        email = email.lower()
    thread = threading.Thread(target=wait_list_user_inv, args=(email, first_name,))
    thread.start()
    logger.debug(f"investor wait list email sent: {email}")
    return jsonify({"result": True, "message": "email sent if the user exists"})


#<==================================================================================================>
#                                    MIME FILE UPLOAD
#<==================================================================================================>
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
        return jsonify({"message": False, "error": "missing key data"})

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
            return jsonify({"message": False, "error": "image file required"})
    else:
        shutil.rmtree(file_location)
        return jsonify({"message": False, "error": "invalid file type"})


#<==================================================================================================>
#                                      DASHBOARD
#<==================================================================================================>
@investor_blueprint.route('/dashboard', methods=["GET", "POST"])
@jwt_required
def investors_dashboard():
    if request.method == "GET":
        jwt_decode = investor_jwt_decoder(get_jwt_identity())
        if not jwt_decode["result"]:
            return jsonify(jwt_decode)

        user_obj = jwt_decode["user_obj"]
        matching_obj = get_inv_matching_data(user_obj.email)

        if matching_obj == {}:
            return {"result": False, "error": "no match found"}

        _id = matching_obj.get("_id")

        if not _id:
            return {"result": False, "error": "no id found"}

        discover = get_discover(_id)

        if not discover["result"]:
            return {"result": False, "error": "no match found"}

        elif discover["result"] and discover["data"] == []:
            return {"result": False, "error": "no match found"}

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

        user_id = response["data"]["user_id"]

        str_obj = Startup.objects.filter(id=user_id).first()
        if not str_obj:
            return jsonify({"result": False, "error": "user does not exist"})

        str_email = str_obj.email
        str_invite = response["data"]["invite"]

        if inv_obj.connected.get(str_email):
            return jsonify({"result": False, "error": "already connected"})

        if not str_invite:

            if not response["data"].get("feedback"):
                return jsonify({"result": False, "error": "feedback is mandotory"})

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

            inv_transactional_replicas = inv_mutual_updates(inv_obj)
            str_transactional_replicas = str_mutual_updates(str_obj)

            if not inv_transactional_replicas:
                technical_errors("INVESTOR: DASHBOARD UPDATE UNSUCCESSFUL", inv_obj.email)

            if not str_transactional_replicas:
                technical_errors("INVESTOR: DASHBOARD UPDATE UNSUCCESSFUL", str_obj.email)

            str_matching_obj = get_str_matching_data(str_email)
            str_id = str_matching_obj.get("_id")

            inv_matching_obj = get_inv_matching_data(inv_email)
            inv_id = inv_matching_obj.get("_id")

            resp = set_response(inv_id, str_id, False)
            if resp.get("status_code") != 200:
                technical_errors("INVESTOR: SET RESPONSE UNSUCCESSFUL", inv_obj.email)

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

                inv_transactional_replicas = inv_mutual_updates(inv_obj)
                str_transactional_replicas = str_mutual_updates(str_obj)

                if not inv_transactional_replicas:
                    technical_errors("INVESTOR: DASHBOARD UPDATE UNSUCCESSFUL", inv_obj.email)

                if not str_transactional_replicas:
                    technical_errors("INVESTOR: DASHBOARD UPDATE UNSUCCESSFUL", str_obj.email)

                def all_info():
                    temp_dict = {}
                    temp_dict["str_bio"] = str_obj.bio
                    temp_dict["inv_fn"] = inv_obj.first_name
                    temp_dict["str_fn"] = str_obj.first_name
                    temp_dict["str_cn"] = str_obj.company_name
                    temp_dict["str_seeking"] = str_obj.round_size
                    temp_dict["str_pitch"] = str_obj.startup_pitch
                    temp_dict["str_founders"] = str_obj.co_founders[0].get("name")
                    return temp_dict

                email_connected(inv_email, str_email, all_info())

                str_matching_obj = get_str_matching_data(str_email)
                str_id = str_matching_obj.get("_id")

                inv_matching_obj = get_inv_matching_data(inv_email)
                inv_id = inv_matching_obj.get("_id")

                resp = set_response(inv_id, str_id, False)
                if resp.get("status_code") != 200:
                    technical_errors("INVESTOR: SET RESPONSE UNSUCCESSFUL", inv_obj.email)

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

                inv_transactional_replicas = inv_mutual_updates(inv_obj)
                str_transactional_replicas = str_mutual_updates(str_obj)

                if not inv_transactional_replicas:
                    technical_errors("INVESTOR: DASHBOARD UPDATE UNSUCCESSFUL", inv_obj.email)

                if not str_transactional_replicas:
                    technical_errors("INVESTOR: DASHBOARD UPDATE UNSUCCESSFUL", str_obj.email)

                str_matching_obj = get_str_matching_data(str_email)
                str_id = str_matching_obj.get("_id")

                inv_matching_obj = get_inv_matching_data(inv_email)
                inv_id = inv_matching_obj.get("_id")

                resp = set_response(inv_id, str_id, False)
                if resp.get("status_code") != 200:
                    technical_errors("INVESTOR: SET RESPONSE UNSUCCESSFUL", inv_obj.email)

                return jsonify({"result": True, "message": "invitation"})


#<==================================================================================================>
#                                     HISTORY ALL
#<==================================================================================================>
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


#<==================================================================================================>
#                                     HISTORY CONNECTED
#<==================================================================================================>
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


#<==================================================================================================>
#                                     HISTORY PASSED
#<==================================================================================================>
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


#<==================================================================================================>
#                                    HISTORY PASSED REVISIT
#<==================================================================================================>
@investor_blueprint.route('/history-profile-view', methods=["POST"])
@jwt_required
def passed_revisit():
    input_req = request.get_json()
    response = validate_inv_passed_recvisit_schema(input_req)

    if response["result"]:
        user_id = response["data"]["user_id"]
        str_obj = Startup.objects.filter(id=user_id).first()
        if not str_obj:
            return jsonify({"result": False, "error": "user does not exist"})

        ma_schema = StartupDashboardSchema()
        data = ma_schema.dump(str_obj)
        return jsonify({"result": True, "data": data})
    else:
        return jsonify(response)


#<==================================================================================================>
#                               CHANGE PASSWORD (PROFILE SETTINGS)
#<==================================================================================================>
@investor_blueprint.route('/change-password', methods=["GET"])
@jwt_required
def change_password():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    inv_obj = jwt_decode["user_obj"]
    if inv_obj is not None:
        token = serial.dumps(inv_obj.email, salt='email_reset')
        link = url_for('investor.reset_link', token=token, _external=True)
        inv_obj.password_reset_meta_data = {"is_clicked": False}
        inv_obj.save()

        thread = threading.Thread(target=password_reset_email, args=(inv_obj.email, link,))
        thread.start()
        logger.debug(f"investor password reset link sent: {inv_obj.email}")
        return jsonify({"result": True, "message": "email sent if the user exists"})
    else:
        return jsonify({"result": False, "error": "user does not exists"})


#<==================================================================================================>
#                                    COMPANY IMAGE API
#<==================================================================================================>
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


#<==================================================================================================>
#                                    VERIFY PASSOWRD :=> DELETE ACCOUNT
#<==================================================================================================>
@investor_blueprint.route('/verify-password', methods=["POST"])
@jwt_required
def verify_password():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    inv_obj = jwt_decode["user_obj"]
    response = validate_delete_acc_schema(request.get_json())
    if response["result"]:
        password = response["data"]["password"]
        if check_password_hash(inv_obj.password, password):
            return jsonify({"result": True, "message": "correct credentials"})
        return jsonify({"result": False, "message": "wrong credentials"})
    return jsonify(response)


#<==================================================================================================>
#                                    FINAL DELETE :=> DELETE ACCOUNT
#<==================================================================================================>
@investor_blueprint.route('/delete-account', methods=["POST"])
@jwt_required
def delete_account():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)


    inv_obj = jwt_decode["user_obj"]
    response = validate_delete_acc_conf_schema(request.get_json())
    if response["result"]:
        delete = response["data"]["delete"]
        if delete:
            setattr(inv_obj, "delete_account", delete)
            inv_obj.save()

            matching_obj = get_inv_matching_data(inv_obj.email)
            str_id = matching_obj.get("_id")
            if not delete_user_ml(str_id):
                technical_errors("INVESTOR: DELETE API UNSUCCESSFUL", inv_obj.email)

            thread = threading.Thread(target=delete_user_account, args=(inv_obj.email, ))
            thread.start()
            logger.debug(f"investor delete account email sent: {inv_obj.email}")

            return jsonify({"result": True, "message": "account deleted"})
        return jsonify({"result": False, "message": "account not deleted"})
    return jsonify(response)


#<==================================================================================================>
#                                  IS JWT TOKEN EXPIRED CHECK
#<==================================================================================================>
@investor_blueprint.route('/jwt-token-check', methods=["GET"])
@jwt_required
def expired_jwt_token_check():
    """
     checks whether a JWT token is expired

     : param ==> None
     : rparam ==> obj (whether or not token is expired)
     """
    resp_obj = {
        "result": True,
        "message": "token is valid"
    }
    return jsonify(resp_obj)


#<==================================================================================================>
#                                  GET JWT TOKEN FOR CONFIRMATION PAGE
#<==================================================================================================>
@investor_blueprint.route('/get-jwt-token', methods=['POST'])
def jwt_for_confirmation_page():
    """
    This is a function to create a user jwt token from email address.

    :param: email
    :return: jwt token
    """
    input_request = request.get_json()
    response = validate_email_schema(input_request)
    if response["result"]:
        email = response["data"]["email"]

        if email:
            email = email.lower()

        user = Investor.objects.filter(email=email).first()
        if user is None:
            error = "user does not exist"
            logger.debug(f"Investor does not exist: {email}")
            return jsonify({"result": False, "error": error})

        jwt_obj = {"email": email, "model": "Investor"}
        access_token = create_access_token(identity=jwt_obj)
        ret_obj = {
            "result": True,
            "token": access_token
        }
        return jsonify(ret_obj)
    else:
        return jsonify(response)


#<==================================================================================================>
#                                       DELETE EMAIL ADDRESSES
#<==================================================================================================>
@investor_blueprint.route('/delete-email-address', methods=['POST'])
def delete_email_address():
    """
    This is a function to delete email address from the startup and investor
    from the main server for testing purpose.

    :param: emails_list
    :type:  list

    :return: result
    :type:   dict
    """

    def db_details(database, collection):
        from pymongo import MongoClient
        remote_mongo_uri = CONSTANT.CURRENT_DATABASE.value
        mongo_client = MongoClient(remote_mongo_uri)
        db = mongo_client[database]
        collection = db[collection]
        return collection

    input_request = request.get_json()
    emails_list = input_request.get("emails_list")
    api_key = input_request.get("api_key")

    if api_key != "***REMOVED***`NqU":
        return jsonify({"result": False, "error": "Invalid API key"})

    if not emails_list:
        return jsonify({"result": False, "error": "emails list not present in the input body"})

    ml_collection = db_details("matching", "users")
    inv_collection = db_details("admin", "investor")
    str_collection = db_details("admin", "startup")

    for email in emails_list:
        my_query = {"email": email}

        ml_query = ml_collection.find_one(my_query)
        inv_query = inv_collection.find_one(my_query)
        str_query = str_collection.find_one(my_query)

        if ml_query:
            ml_collection.delete_many(my_query)
            print("User Deleted from Machine Learning")

        if str_query:
            str_collection.delete_one(my_query)
            print("User Deleted from Startup")

        if inv_query:
            inv_collection.delete_one(my_query)
            print("User Deleted from Investors")

    return jsonify({"result": True, "message": "All emails deleted if existed"})


#<==================================================================================================>
#                                    STRING TO EMAIL MAPPING
#<==================================================================================================>
@investor_blueprint.route('/ste-mapping', methods=['POST'])
def string_to_email_mapping():
    """
    This is a function to return the respective emails from the string values

    :param: string_id
    :type:  string

    :return: email
    :type:   string
    """

    input_req = request.get_json()
    response = validate_inv_passed_recvisit_schema(input_req)

    if response["result"]:
        user_id = response["data"]["user_id"]
        str_obj = Startup.objects.filter(id=user_id).first()
        if not str_obj:
            return jsonify({"result": False, "error": "user does not exist"})
        else:
            email = str_obj.email
            return jsonify({"result": True, "email": email})
    return response


#<==================================================================================================>
#                                    ANGEL GROUP NAME SEARCH
#<==================================================================================================>
@investor_blueprint.route('/angelgroup-name-search', methods=['POST'])
def angel_group_name_search():
    """
    This is a test function to return the matching values of angel group from the AG database

    :param: name
    :type:  string

    :return: complete matching name
    :type:   string
    """

    input_req = request.get_json()
    response = validate_inv_angel_group_name_schema(input_req)
    if response["result"]:
        import re
        regex_obj = re.compile(f".*{response['data']['angel_group_name']}.*")
        matching_objs = AngelGroup.objects(name=regex_obj)
        if matching_objs:
            final_resp = {
                "result": True,
                "data": [i.name for i in matching_objs]
            }
            return jsonify(final_resp)
        return jsonify({"result": False, "data": None})
    return response