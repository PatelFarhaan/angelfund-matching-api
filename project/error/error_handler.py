from flask import Blueprint, jsonify


errorpage_blueprint = Blueprint('error', __name__)

@errorpage_blueprint.app_errorhandler(403)
def error_403(e):
    return_obj = {
        "result": False,
        "status_code": 403,
        "message": "forbidden access"
    }
    return jsonify(return_obj)


@errorpage_blueprint.app_errorhandler(404)
def error_404(e):
    return_obj = {
        "result": False,
        "status_code": 404,
        "message": "page not found",
    }
    return jsonify(return_obj)


@errorpage_blueprint.app_errorhandler(405)
def error_405(e):
    return_obj = {
        "result": False,
        "status_code": 405,
        "message": "method not allowed",
    }
    return jsonify(return_obj)


@errorpage_blueprint.app_errorhandler(500)
def error_500(e):
    return_obj = {
        "result": False,
        "status_code": 500,
        "message": "internal server error"
    }
    return jsonify(return_obj)