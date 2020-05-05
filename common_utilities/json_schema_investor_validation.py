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

inv_company_schema = {
    "type": "object",
    "properties": {
        "company_name": {
            "type": "string"
        },
    },
    "required": ["company_name"],
    "additionalProperties": False
}


def validate_company_schema(data):
    try:
        validate(instance=data, schema= inv_company_schema)
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
inv_monday_notification_schema = {
    "type": "object",
    "properties": {
        "monday_notification": {
            "type": "boolean",
        },
    },
    "required": ["monday_notification"],
    "additionalProperties": False
}


def validate_inv_monday_notification_schema(data):
    try:
        validate(instance=data, schema= inv_monday_notification_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}
#############################################################################################################################################
inv_delete_acc_schema = {
    "type": "object",
    "properties": {
        "password": {
            "type": "string",
        },
    },
    "required": ["password"],
    "additionalProperties": False
}


def validate_delete_acc_schema(data):
    try:
        validate(instance=data, schema= inv_delete_acc_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}
#############################################################################################################################################

inv_invite_accepted_notification_schema = {
    "type": "object",
    "properties": {
        "invite_notification": {
            "type": "boolean",
        },
    },
    "required": ["invite_notification"],
    "additionalProperties": False
}


def validate_invite_acc_notify_schema(data):
    try:
        validate(instance=data, schema= inv_invite_accepted_notification_schema)
    except ValidationError as e:
        return {'result': False, 'message': e.message}
    except SchemaError as e:
        return {'result': False, 'message': e.message}
    return {'result': True, 'data': data}
#############################################################################################################################################
