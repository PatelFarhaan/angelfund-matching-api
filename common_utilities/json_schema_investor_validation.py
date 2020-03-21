from jsonschema import validate
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import ValidationError

#############################################################################################################################################

inv_first_page_schema = {
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

def validate_inv_first_page_schema(data):
    try:
        validate(instance=data, schema=inv_first_page_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}

#############################################################################################################################################

inv_login_schema = {
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

def validate_inv_login_schema(data):
    try:
        validate(instance=data, schema=inv_login_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}

#############################################################################################################################################

inv_password_reset_schema = {
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

def validate_inv_password_reset_schema(data):
    try:
        validate(instance=data, schema= inv_password_reset_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}

#############################################################################################################################################

inv_email_schema = {
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
        validate(instance=data, schema= inv_email_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}

#############################################################################################################################################

