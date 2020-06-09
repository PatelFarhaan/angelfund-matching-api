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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}

#############################################################################################################################################

inv_dashboard_schema = {
    "type": "object",
    "properties": {
        "user_id": {
            "type": "string",
            "minLength": 24,
            "maxLength": 24
        },
        "invite": {
            "type": "boolean"
        },
    },
    "required": ["user_id", "invite"],
}


def validate_dashboard_schema(data):
    try:
        validate(instance=data, schema= inv_dashboard_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}
#############################################################################################################################################
inv_profile_vis_schema = {
    "type": "object",
    "properties": {
        "visible": {
            "type": "boolean",
        },
    },
    "required": ["visible"],
    "additionalProperties": False
}


def validate_profile_vis_schema(data):
    try:
        validate(instance=data, schema= inv_profile_vis_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}
#############################################################################################################################################
str_rmeove_slide_deck_schema = {
    "type": "object",
    "properties": {
        "remove_slide_deck": {
            "type": "boolean",
        },
    },
    "required": ["remove_slide_deck"],
    "additionalProperties": False
}


def validate_remove_slide_deck_schema(data):
    try:
        validate(instance=data, schema= str_rmeove_slide_deck_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}
#############################################################################################################################################
