from jsonschema import validate
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import ValidationError

#############################################################################################################################################

str_first_page_schema = {
    "type": "object",
    "properties": {
        "first_name": {
            "type": "string",
        },
        "last_name": {
            "type": "string"
        },
        "password": {
            "type": "string",
            "minLength": 8
        },
        "email": {
            "type": "string",
            "format": "email"
        }
    },
    "required": ["first_name", "last_name", "email", "password"],
    "additionalProperties": False
}

def validate_str_first_page_schema(data):
    try:
        validate(instance=data, schema=str_first_page_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}

#############################################################################################################################################

str_login_schema = {
    "type": "object",
    "properties": {
        "password": {
            "type": "string",
            "minLength": 8
        },
        "email": {
            "type": "string",
            "format": "email"
        }
    },
    "required": ["email", "password"],
    "additionalProperties": False
}

def validate_str_login_schema(data):
    try:
        validate(instance=data, schema=str_login_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}

#############################################################################################################################################

str_password_reset_schema = {
    "type": "object",
    "properties": {
        "password": {
            "type": "string",
            "minLength": 8
        }
    },
    "required": ["password"],
    "additionalProperties": False
}

def validate_str_password_reset_schema(data):
    try:
        validate(instance=data, schema= str_password_reset_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}

#############################################################################################################################################

str_email_schema = {
    "type": "object",
    "properties": {
        "email": {
            "type": "string",
            "format": "email"
        }
    },
    "required": ["email"],
    "additionalProperties": False
}


def validate_email_schema(data):
    try:
        validate(instance=data, schema= str_email_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}

#############################################################################################################################################

inv_google_schema = {
    "type": "object",
    "properties": {
        "token": {
            "type": "string"
        }
    },
    "required": ["token"],
    "additionalProperties": False
}


def validate_google_schema(data):
    try:
        validate(instance=data, schema= inv_google_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}

#############################################################################################################################################

inv_dashboard_schema = {
    "type": "object",
    "properties": {
        "email": {
            "type": "string",
            "format": "email"
        },
        "invite": {
            "type": "boolean"
        },
    },
    "required": ["email", "invite"],
    "additionalProperties": False
}


def validate_dashboard_schema(data):
    try:
        validate(instance=data, schema= inv_dashboard_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}

#############################################################################################################################################

inv_referrer_schema = {
    "type": "object",
    "properties": {
        "email": {
            "type": "string",
            "format": "email"
        },
    },
    "required": ["email"],
    "additionalProperties": False
}


def validate_referrer_schema(data):
    try:
        validate(instance=data, schema= inv_referrer_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}

#############################################################################################################################################

inv_passed_recvisit_schema = {
    "type": "object",
    "properties": {
        "email": {
            "type": "string",
            "format": "email"
        },
    },
    "required": ["email"],
    "additionalProperties": False
}


def validate_inv_passed_recvisit_schema(data):
    try:
        validate(instance=data, schema= inv_passed_recvisit_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}
#############################################################################################################################################