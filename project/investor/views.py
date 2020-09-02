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
from common_utilities.jwt_decoder import investor_jwt_decoder
from common_utilities.company_images import company_images_api
from common_utilities.emails.referral_email import email_referral
from project.models import Investor, Startup, Referrals, AngelGroup
from common_utilities.emails.connected_emails import email_connected
from project.investor.marshmallow_serialize import InvestorUserSchema
from common_utilities.emails.password_reset import password_reset_email
from common_utilities.mime_files_upload import profile_pic_upload_to_s3
from werkzeug.security import generate_password_hash, check_password_hash
from common_utilities.emails.email_confirmation import email_confirmation
from common_utilities.emails.google_email import google_email_confirmation
from common_utilities.emails.wait_list_email_inv import wait_list_user_inv
from common_utilities.data_processing.startup_dp import get_all_startup_data
from common_utilities.common_mappings import sector_data, accreditation_data
from common_utilities.emails.account_delete_email import delete_user_account
from common_utilities.analytics.user_signin_analytics import login_analytics
from common_utilities.analytics.user_signup_analytics import signup_analytics
from flask import url_for, request, Blueprint, jsonify, redirect, session, render_template
from common_utilities.reverse_common_mapping import rev_accreditation_data, rev_sector_data
from common_utilities.flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from project.startup.marshmallow_serialize import StartupConnectedSchema, StartupPassedSchema, StartupDashboardSchema
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
                        logger.debug(f"investor: google-token: logged in: {email}")

                        analytics_thread = threading.Thread(target=login_analytics, args=(email, True,))
                        analytics_thread.start()

                        ma_schema = InvestorUserSchema()
                        user_objs = ma_schema.dump(user)
                        user_objs["email"] = email

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

                        user = Investor.objects.filter(email=email).first()
                        logger.debug(f"investor: google-token: created via Google OAuth: {email}")

                        thread = threading.Thread(target=google_email_confirmation, args=(user,))
                        thread.start()

                        user = Investor.objects.filter(email=email).first()
                        login_user(user)
                        user.is_logged_in = True
                        user.save()
                        logger.debug(f"investor: google-token: logged in: {email}")

                        ma_schema = InvestorUserSchema()
                        user_objs = ma_schema.dump(user)

                        signup_analytics_thread = threading.Thread(target=signup_analytics, args=(True,))
                        signup_analytics_thread.start()

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
                    logger.debug(f"investor: google-token: {message}: {userinfo_response.json().get('email', 'email_not_mentioned')}")
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
            logger.debug(f"investor: login: does not exist: {email}")
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
            thread = threading.Thread(target=email_confirmation, args=(user, link, user.first_name))
            thread.start()
            return jsonify({"result": False, "error": error})

        if user and check_password_hash(user.password, password):
            if getattr(user, "delete_account"):
                return jsonify({"result": False, "error": "account deleted"})

            login_user(user)
            user.is_logged_in = True
            user.save()
            logger.debug(f"investor: login: logged in: {email}")

            analytics_thread = threading.Thread(target=login_analytics, args=(email, True,))
            analytics_thread.start()

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
            logger.debug(f"investor: login: wrong credentials: {email}")
            return jsonify({"result": False, "error": "wrong credentials"})
    else:
        return jsonify(response)


#<==================================================================================================>
#                                      PASSWORD RESET LINK
#<==================================================================================================>
@investor_blueprint.route('/reset-link/<token>', methods=['GET', 'POST'])
def reset_link(token):
    if request.method == "GET":
        return render_template("reset.html")

    elif request.method == "POST":
        try:
            email = serial.loads(token, salt='email_reset', max_age=int(CONSTANT.PASSWORD_RESET_LINK_AGE.value))
            logger.debug(f"investor: reset-link/token: reset password link clicked: {email}")
            if email:
                user_obj = Investor.objects.filter(email=email).first()
                user_obj.is_logged_in = False
                user_obj.save()
                logger.debug(f"investor: reset-link/token: user logged out: {email}")
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
                logger.debug(f"investor: reset-link/token: password changed: {email}")
                return render_template("reset-success-inv.html")
        else:
            logger.debug(f"investor: reset-link/token: user does not exist: {email}")
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
            logger.debug(f"investor: forgot-password: user does not exist : {email}")
            return jsonify({"result": True, "message": "email sent if the user exists"})

        token = serial.dumps(user.email, salt='email_reset')
        link = url_for('investor.reset_link', token=token, _external=True)
        user.password_reset_meta_data = {"is_clicked": False}
        user.save()
        logger.debug(f"investor: forgot-password: forgot password link generated: {email}")


        thread = threading.Thread(target=password_reset_email, args=(email, link,))
        thread.start()
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
            logger.debug(f"investor: register: exists: {email}")
            error = "email exists"
            return jsonify({"result": False, "error": error})

        input_request["password"] = generate_password_hash(input_request["password"])

        if input_request.get("email"):
            input_request["email"] = input_request["email"].lower()
        new_user = Investor(**input_request)
        new_user.save()

        user = Investor.objects.filter(email=email).first()
        logger.debug(f"investor: register: created {email}")

        token = serial.dumps(email, salt='email_confirm')
        link = url_for('investor.email_confirmed', token=token, _external=True)
        thread = threading.Thread(target=email_confirmation, args=(new_user, link, input_request.get("first_name")))
        thread.start()

        signup_analytics_thread = threading.Thread(target=signup_analytics, args=(True,))
        signup_analytics_thread.start()

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
        logger.debug(f"investor: email-confirmed: email confirmation link clicked: {email}")
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
            logger.debug(f"investor: email-confirmed: email confirmed: {email}")

        login_user(user)
        user.is_logged_in = True
        user.passowrd_confirm_meta_data = {}
        user.save()
        session["email"] = email

        logger.debug(f"investor: email-confirmed: logged in: {email}")
        return redirect(url_for("investor.confirmation_signup_flow", email=email, code=302))

    else:
        logger.debug(f"investor: email-confirmed: user does not exist {email}")
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
        logger.debug(f"investor: confirmation-signup-flow: email not in session: {email}")
        return jsonify({"reuslt": False, "error": "session expired"})

    inv_obj = Investor.objects.filter(email=email).first()
    first_name = (inv_obj.first_name).strip().replace(" ", "_")
    last_name = (inv_obj.last_name).strip().replace(" ", "_")
    query_string = f"confirmed=True&email={inv_obj.email}&fn={first_name}&ln={last_name}&investor=true"
    logger.debug(f"investor: confirmation-signup-flow: redirect to onboarding flow: {email}")
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
    logger.debug(f"investor: logout: user logged out: {user_obj.email}")
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
        logger.debug(f"investor: referral-link: referral email exists on investors model: {ref_email}")
        return jsonify({"result": False, "error": "user exists"})

    if Startup.objects.filter(email=ref_email).first():
        logger.debug(f"investor: referral-link: referral email exists on startup model: {ref_email}")
        return jsonify({"result": False, "error": "user exists"})

    full_name = user_obj.first_name + " " + user_obj.last_name
    first_name = user_obj.first_name

    ref_obj = {"referred_by": user_obj.email, "referred": ref_email}
    logger.info(f"investor: referral-link: {ref_email} is referred by {user_obj.email}")

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
        ref_by_obj = Referrals.objects.filter(email=user.email).first()
        if ref_by_obj:
            details = dict(ref_by_obj.details)
            referred_to = list(details.get("referred_to"))
            if referred in referred_to:
                logger.debug(f"investor: referral: {referred} is already referred by {referred_by}")
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
            logger.debug(f"investor: referral: {referred} is already referred by {referred_by}")
            return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)

        details = {
            "referred_by": referred_by,
            "referred_to": []
            }
        new_ref_obj = Referrals(email=referred, details=details)
        new_ref_obj.save()

        logger.debug(f"investor: referral: {referred} is referred by {referred_by}")
        return redirect(f"{CONSTANT.CURRENT_SERVER.value}", code=302)
    else:
        logger.debug(f"investor: referral: startup does not exist {referred_by}")
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
                logger.debug(f"investor: update-info: {key} key does not exist in available fields: {user_obj.email}")
                return jsonify({"result": False, "error": "invalid user field"})

        for field in input_data:
            if field in available_fields:
                if field == "sectors":
                    sectors_map = sector_data()
                    res = [ sectors_map.get(i) for i in input_data[field] if sectors_map.get(i) != None ]
                    setattr(user_obj, field, res)
                    logger.info(f"investor: update-info: {field } updated to {res}: {user_obj.email}")

                elif field == "accreditation":
                    accreditation_map = accreditation_data()
                    res = accreditation_map.get(input_data[field])
                    setattr(user_obj, field, res)
                    logger.info(f"investor: update-info: {field} updated to {res}: {user_obj.email}")

                else:
                    setattr(user_obj, field, input_data[field])
                    logger.info(f"investor: update-info: {field} updated to {input_data[field]}: {user_obj.email}")

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
            inp_data = response["data"]["monday_notification"]
            setattr(inv_obj, "monday_notification", inp_data)
            inv_obj.save()
            logger.debug(f"investor: monday-notifications: monday notification set to {inp_data}: {inv_obj.email}")

            return jsonify({"result": True, "message": "value updated"})
        else:
            return jsonify(response)


#<==================================================================================================>
#                                    PRIOR INVESTMENT CHECK
#<==================================================================================================>
@investor_blueprint.route('/prior-investment-check', methods=["GET"])
@jwt_required
def prior_investment_check():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    inv_obj = jwt_decode["user_obj"]

    if not inv_obj.prior_investments:
        inv_obj.prior_inv_completed = False
        inv_obj.save()
        logger.debug(f"investor: prior-investment-check: prior investments empty for: {inv_obj.email}")
        logger.debug(f"investor: prior-investment-check: show profile field set to False: {inv_obj.email}")
        return jsonify({"result": False, "message": "prior investment field is empty"})

    inv_obj.prior_inv_completed = True
    inv_obj.save()
    logger.debug(f"investor: prior-investment-check: prior investments not empty for: {inv_obj.email}")
    logger.debug(f"investor: prior-investment-check: show profile field set to True: {inv_obj.email}")
    return jsonify({"result": True, "message": "prior investment field is not empty"})


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
        logger.debug(f"investor: profile-visibility: profile visibility set to {visible}: {inv_obj.email}")
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
            logger.debug(f"investor: mime-files: profile pic updated: {user_obj.email}")
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
        cards = user_obj.discover_cards
        str_data = get_all_startup_data(cards)
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
                logger.debug(f"investor: dashboard: feedback is mandatory: {inv_obj.email}")
                return jsonify({"result": False, "error": "feedback is mandatory"})

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

                def all_info():
                    temp_dict = {}
                    temp_dict["inv_fn"] = inv_obj.first_name
                    temp_dict["str_fn"] = str_obj.first_name
                    temp_dict["str_cn"] = str_obj.company_name
                    temp_dict["str_seeking"] = str_obj.round_size
                    temp_dict["str_pitch"] = str_obj.startup_pitch
                    temp_dict["str_founders"] = str_obj.co_founders[0].get("name")
                    return temp_dict

                email_connected(inv_email, str_email, all_info())
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


#<==================================================================================================>
#                                     HISTORY ALL
#<==================================================================================================>
@investor_blueprint.route('/history-all', methods=["GET"])
@jwt_required
def history():
    def get_passed_feedback(str_email: str, inv_email: str):
        str_obj = Startup.objects.filter(email=str_email).first()
        if str_obj:
            inv_feedback = dict(getattr(str_obj, "feedback")).get(inv_email)
            return inv_feedback
        else:
            return None

    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    data = []
    inv_obj = jwt_decode["user_obj"]

    # passed
    passed = getattr(inv_obj, "passed")
    print(passed)
    ma_schema = StartupPassedSchema()
    for k, v in passed.items():
        str_obj = Startup.objects.filter(email=k).first()
        passed_str_data = ma_schema.dump(str_obj)
        investors_feedback = get_passed_feedback(k, inv_obj.email)
        if investors_feedback:
            passed_str_data["feedback"] = investors_feedback
            data.append(passed_str_data)

    # connected
    connected = getattr(inv_obj, "connected")
    ma_schema = StartupConnectedSchema()
    for k, v in connected.items():
        str_obj = Startup.objects.filter(email=k).first()
        data.append(ma_schema.dump(str_obj))

    logger.debug(f"investor: history-all: data found: {inv_obj.email}")
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

    logger.debug(f"investor: history-connected: data found: {inv_obj.email}")
    return jsonify({"result": True, "data": data})


#<==================================================================================================>
#                                     HISTORY PASSED
#<==================================================================================================>
@investor_blueprint.route('/history-passed', methods=["GET"])
@jwt_required
def passed():
    def get_passed_feedback(str_email: str, inv_email: str):
        str_obj = Startup.objects.filter(email=str_email).first()
        inv_feedback = dict(getattr(str_obj, "feedback")).get(inv_email)
        return inv_feedback

    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    inv_obj = jwt_decode["user_obj"]

    passed = getattr(inv_obj, "passed")
    ma_schema = StartupPassedSchema()
    data = []
    for k, v in passed.items():
        str_obj = Startup.objects.filter(email=k).first()
        passed_str_data = ma_schema.dump(str_obj)
        passed_str_data["feedback"] = get_passed_feedback(k, inv_obj.email)
        data.append(passed_str_data)

    logger.debug(f"investor: history-passed: data found: {inv_obj.email}")
    return jsonify({"result": True, "data": data})


#<==================================================================================================>
#                                    HISTORY PASSED REVISIT
#<==================================================================================================>
@investor_blueprint.route('/history-profile-view', methods=["POST"])
@jwt_required
def passed_revisit():
    jwt_decode = investor_jwt_decoder(get_jwt_identity())
    if not jwt_decode["result"]:
        return jsonify(jwt_decode)

    inv_obj = jwt_decode["user_obj"]

    input_req = request.get_json()
    response = validate_inv_passed_recvisit_schema(input_req)

    if response["result"]:
        user_id = response["data"]["user_id"]
        str_obj = Startup.objects.filter(id=user_id).first()
        if not str_obj:
            return jsonify({"result": False, "error": "user does not exist"})

        ma_schema = StartupDashboardSchema()
        data = ma_schema.dump(str_obj)
        logger.debug(f"investor: history-profile-view: data found: {inv_obj.email}")
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
        logger.debug(f"investor: change-password: password link generated: {inv_obj.email}")

        thread = threading.Thread(target=password_reset_email, args=(inv_obj.email, link,))
        thread.start()
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

        user_obj = jwt_decode["user_obj"]

        inp_req = request.get_json()
        response = validate_company_schema(inp_req)

        if not response["result"]:
            return jsonify(response)

        company_name = response["data"]["company_name"]
        logger.debug(f"investor: company-image-api: {company_name} searched by: {user_obj.email}")
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
            logger.debug(f"investor: verify-password: correct password: {inv_obj.email}")
            return jsonify({"result": True, "message": "correct credentials"})
        logger.debug(f"investor: verify-password: wrong password: {inv_obj.email}")
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
            logger.debug(f"investor: delete-account: account deleted: {inv_obj.email}")

            thread = threading.Thread(target=delete_user_account, args=(inv_obj.email, ))
            thread.start()

            return jsonify({"result": True, "message": "account deleted"})
        return jsonify({"result": False, "message": "account not deleted"})
    return jsonify(response)


#<==================================================================================================>
#                                  IS JWT TOKEN EXPIRED CHECK
#<==================================================================================================>
@investor_blueprint.route('/jwt-token-check', methods=["GET"])
@jwt_required
def expired_jwt_token_check():
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
    input_request = request.get_json()
    response = validate_email_schema(input_request)
    if response["result"]:
        email = response["data"]["email"]

        if email:
            email = email.lower()

        user = Investor.objects.filter(email=email).first()
        if user is None:
            error = "user does not exist"
            logger.debug(f"investor: get-jwt-token: {error}: {email}")
            return jsonify({"result": False, "error": error})

        jwt_obj = {"email": email, "model": "Investor"}
        access_token = create_access_token(identity=jwt_obj)
        ret_obj = {
            "result": True,
            "token": access_token
        }
        logger.debug(f"investor: get-jwt-token: new jwt token generated: {email}")
        return jsonify(ret_obj)
    else:
        return jsonify(response)


#<==================================================================================================>
#                                       DELETE EMAIL ADDRESSES
#<==================================================================================================>
@investor_blueprint.route('/delete-email-address', methods=['POST'])
def delete_email_address():
    def db_details(database, collection):
        from pymongo import MongoClient
        remote_mongo_uri = CONSTANT.CURRENT_DATABASE.value
        mongo_client = MongoClient(remote_mongo_uri)
        db = mongo_client[database]
        collection = db[collection]
        return collection

    if request.method == "POST":
        input_request = request.get_json()
        emails_list = input_request.get("emails_list")
        api_key = input_request.get("api_key")

        if api_key != "***REMOVED***`NqU":
            logger.debug(f"investor: delete-email-address: invalid api key: angelfund-team")
            return jsonify({"result": False, "error": "Invalid API key"})

        if not emails_list:
            logger.debug(f"investor: delete-email-address: email address not present in input body: angelfund-team")
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
                logger.debug(f"investor: delete-email-address: email address deleted from ML model: {email}: angelfund-team")
                print("User Deleted from Machine Learning")

            if str_query:
                str_collection.delete_one(my_query)
                logger.debug(f"investor: delete-email-address: email address deleted from startup model: {email}: angelfund-team")

            if inv_query:
                inv_collection.delete_one(my_query)
                logger.debug(f"investor: delete-email-address: email address deleted from investor model: {email}: angelfund-team")

        return jsonify({"result": True, "message": "All emails deleted if existed"})


#<==================================================================================================>
#                                    STRING TO EMAIL MAPPING
#<==================================================================================================>
@investor_blueprint.route('/ste-mapping', methods=['POST'])
def string_to_email_mapping():
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