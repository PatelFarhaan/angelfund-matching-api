import threading
from project import serial
from common_utilities import CONSTANT
from project.users.models import Users
from flask import url_for, request, Blueprint, jsonify
from common_utilities.file_upload_to_s3 import file_upload_to_s3
from common_utilities.password_reset import password_reset_email
from common_utilities.email_confirmation import email_confirmation
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from common_utilities.secondary_mongo_read import search_single_obj_in_database, search_multiple_obj_in_database


users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', None)
        password = request.form.get('password', None)

        if email is None:
            return return_none_results("email")
        if password is None:
            return return_none_results("password")

        user = Users.objects.filter(email=email).first()
        if user is None:
            message = "user does not exist"
            return return_data_results(False, message)

        if not user.email_confirmed:
            message = "please confirm your email address"
            token = serial.dumps(email, salt='email_confirm')
            link = url_for('users.email_confirmed', token=token, _external=True)
            thread = threading.Thread(target=email_confirmation, args=(email, link,))
            thread.start()
            return return_data_results(False, message)

        if user and check_password_hash(user.password, password):
            login_user(user)
            # generate jwt token
            message = "user logged in successfully"
            return return_data_results(True, message)
        else:
            message = "wrong credentails"
            return return_data_results(False, message)

    elif request.method == "GET":
        message = "frontend user login template"
        return return_data_results(True, message)


@users_blueprint.route('/username_login', methods=['GET','POST'])
def username_login():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        if username is None:
            return return_none_results("username")
        if password is None:
            return return_none_results("password")

        user = Users.objects.filter(username=username).first()
        if user is None:
            message = "user does not exist"
            return return_data_results(False, message)

        email = user.email
        if not user.email_confirmed:
            message = "please confirm your email address"
            token = serial.dumps(email, salt='email_confirm')
            link = url_for('users.email_confirmed', token=token, _external=True)
            thread = threading.Thread(target=email_confirmation, args=(email, link,))
            thread.start()
            return return_data_results(False, message)

        if user and check_password_hash(user.password, password):
            login_user(user)
            # generate jwt token
            message = "user logged in successfully"
            return return_data_results(True, message)
        else:
            message = "wrong credentails"
            return return_data_results(False, message)

    elif request.method == "GET":
        message = "frontend username login template"
        return return_data_results(True, message)


@users_blueprint.route('/reset_link/<token>', methods=['GET','POST'])
def reset_link(token):  # Both click and time based
    try:
        email = serial.loads(token, salt='email_reset', max_age=int(CONSTANT.PASSWORD_RESET_LINK_AGE.value))
        user = Users.objects.filter(email=email).first()
        if user:
            if request.method == 'POST':
                password = request.form.get('password', None)
                if password is None:
                    return return_none_results("password")
                if not user.password_reset_meta_data["is_clicked"]:
                    user.password = generate_password_hash(password)
                    user.password_reset_meta_data = {}
                    user.save()
                    message = "password changed successfully"
                    return return_data_results(True, message)
                else:
                    message = "password reset link expired"
                    return return_data_results(False, message)

            elif request.method == "GET":
                message = "frontend password reset template"
                return return_data_results(True, message)
    except:
        message = "password reset link expired"
        return return_data_results(False, message)


@users_blueprint.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', None)
        if email is None:
            return return_none_results("email")
        user = Users.objects.filter(email=email).first()
        if user is None:
            message = "user does not exist"
            return return_data_results(False, message)
        token = serial.dumps(user.email, salt='email_reset')
        link = url_for('users.reset_link', token=token, _external=True)
        user.password_reset_meta_data = {"is_clicked": False}
        user.save()
        thread = threading.Thread(target=password_reset_email, args=(email, link,))
        thread.start()
        message = "frontend password reset link sent template"
        return return_data_results(True, message)

    elif request.method == "GET":
        message = "frontend forgot password template"
        return return_data_results(True, message)


@users_blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    message = "user logged out successfully"
    return return_data_results(True, message)


@users_blueprint.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', None)
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        last_name = request.form.get('last_name', None)
        first_name = request.form.get('first_name', None)
        profile_photo = request.files.get('profile_pic', None)

        if email is None:
            return return_none_results("email")
        if username is None:
            return return_none_results("username")
        if password is None:
            return return_none_results("password")
        if last_name is None:
            return return_none_results("last_name")
        if first_name is None:
            return return_none_results("first_name")

        email_exist = Users.objects.filter(email=email).first()
        username_exist = Users.objects.filter(username=username).first()

        if email_exist:
            message = "email exists"
            return return_data_results(False, message)
        if username_exist:
            message = "username exists"
            return return_data_results(False, message)

        if profile_photo:
            profile_photo_name = profile_photo.filename.strip().replace(' ', '')
            public_profile_pic_link = file_upload_to_s3(profile_photo, profile_photo_name)
            # noinspection PyArgumentList
            new_user = Users(email=email,
                             username=username,
                             last_name=last_name,
                             first_name=first_name,
                             profile_pic_link=public_profile_pic_link,
                             password=generate_password_hash(password))
            new_user.save()
        else:
            # noinspection PyArgumentList
            new_user = Users(email=email,
                             username=username,
                             last_name=last_name,
                             first_name=first_name,
                             password=generate_password_hash(password))
            new_user.save()


        token = serial.dumps(email, salt='email_confirm')
        link = url_for('users.email_confirmed', token=token, _external=True)
        thread = threading.Thread(target=email_confirmation, args=(email, link,))
        thread.start()
        message = "frontend email confirmation template"
        return return_data_results(True, message)
    
    elif request.method == "GET":
        message = "frontend register template"
        return return_data_results(True, message)


@users_blueprint.route('/email_confirmed/<token>', methods=['GET','POST'])
def email_confirmed(token):
    email = serial.loads(token, salt='email_confirm')
    user = Users.objects.filter(email=email).first()
    if user:
        user.email_confirmed = True
        user.save()
        message = "frontend email confirmed template"
        return return_data_results(True, message)
    else:
        message = "user does not exist"
        return return_data_results(False, message)


@users_blueprint.route('/test', methods=["GET"])
@login_required
def test():
    return jsonify({
        "result": "test",
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