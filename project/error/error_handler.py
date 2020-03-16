from flask import render_template, Blueprint


errorpage_blueprint = Blueprint('error', __name__, template_folder='templates')


@errorpage_blueprint.app_errorhandler(404)
def error_404(e):
    return render_template('error_pages/404.html'), 404


@errorpage_blueprint.app_errorhandler(403)
def error_403(e):
    return render_template('error_pages/403.html')