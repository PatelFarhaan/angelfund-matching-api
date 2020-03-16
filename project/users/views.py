from project import serial
from project.users.models import Users
from common_utilities.password_reset import password_reset_email
from common_utilities.email_confirmation import email_confirmation
from flask import render_template, redirect, url_for, request, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user


users_blueprint = Blueprint('users', __name__, template_folder='templates')


@users_blueprint.route('/username_login', methods=['GET','POST'])
def username_login():
    if request.method == 'POST':
        username = request.get('username', None)
        password = request.get('password', None)
        user = Users.objects.filter(username=username).first()
        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            next = request.args.get('next')
            if next == None or next[0] == '/':
                next = url_for('core.index')
            return redirect(next)
    return render_template('username_login.html')


@users_blueprint.route('/reset_link/<token>', methods=['GET','POST'])
def reset_link(token):
    try:
        email = serial.loads(token, salt='email_reset', max_age=500)
        user = Users.objects.filter(email=email).first_or_404()
        if user:
            if request.method == 'POST':
                password = request.get('password', None)
                user.password = generate_password_hash(password)
                user.save()
                return render_template('password_changed.html')
            return render_template('reset_link.html')
    except:
        return render_template('link_expired.html')


@users_blueprint.route('/reset_link_sent', methods=['GET','POST'])
def reset_link_sent():
    return render_template('reset_link_sent.html')


@users_blueprint.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.get('email', None)
        user = Users.objects.filter(email=email).first_or_404()
        if user:
            token = serial.dumps(user.email, salt='email_reset')
            link = url_for('users.reset_link', token=token, _external=True)
            password_reset_email(email, link)
            return redirect(url_for('users.reset_link_sent'))
    return render_template('forgot_password.html')


@users_blueprint.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.get('email', None)
        password = request.get('password')
        user = Users.objects.filter(email=email).first()
        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            next = request.args.get('next')
            if next == None or next[0] == '/':
                next = url_for('core.index')
            return redirect(next)
        if not user:
            errors = "Invalid Credentials"
    return render_template('login.html')


@users_blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('core.index'))


@users_blueprint.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.get('email', None)
        username = request.get('email', None)
        password = request.get('email', None)
        last_name = request.get('email', None)
        first_name = request.get('email', None)
        # noinspection PyArgumentList
        new_user = Users(email=email,
                         username=username,
                         last_name=last_name,
                         first_name=first_name,
                         password=generate_password_hash(password))
        new_user.save()
        token = serial.dumps(email.data, salt='email_confirm')
        link = url_for('users.email_confirmed', token=token, _external=True)
        email_confirmation(email, link)
        return render_template('email_confirmed_link_sent.html')
    return render_template('register.html')


@users_blueprint.route('/email_confirmed/<token>', methods=['GET','POST'])
def email_confirmed(token):
    email = serial.loads(token, salt='email_confirm')
    user = Users.objects.filter(email=email).first()
    if user:
        user.email_confirmed = True
        user.save()
        return render_template('email_confirmed.html')
    else:
        return render_template('error_pages/404.html')