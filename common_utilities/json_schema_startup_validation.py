#<==================================================================================================>
#                                      IMPORTS
#<==================================================================================================>
from jsonschema import validate
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import ValidationError


#<==================================================================================================>
#                                   STARTUP FIRST PAGE SCHEMA
#<==================================================================================================>
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


#<==================================================================================================>
#                                   STARTUP LOGIN SCHEMA
#<==================================================================================================>
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


#<==================================================================================================>
#                                   STARTUP PASSWORD RESET SCHEMA
#<==================================================================================================>
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


#<==================================================================================================>
#                                   STARTUP EMAIL SCHEMA
#<==================================================================================================>
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


#<==================================================================================================>
#                                   STARTUP GOOGLE SCHEMA
#<==================================================================================================>
str_google_schema = {
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
        validate(instance=data, schema= str_google_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                                   STARTUP DASHBOARD SCHEMA
#<==================================================================================================>
str_dashboard_schema = {
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
        validate(instance=data, schema=str_dashboard_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                                   STARTUP REFERRAL SCHEMA
#<==================================================================================================>
str_referrer_schema = {
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
        validate(instance=data, schema=str_referrer_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                               STARTUP MONDAY NOTIFICATION SCHEMA
#<==================================================================================================>
str_monday_notification_schema = {
    "type": "object",
    "properties": {
        "monday_notification": {
            "type": "boolean",
        },
    },
    "required": ["monday_notification"],
    "additionalProperties": False
}

def validate_str_monday_notification_schema(data):
    try:
        validate(instance=data, schema=str_monday_notification_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                                   STARTUP DELETE ACCOUNT SCHEMA
#<==================================================================================================>
str_delete_acc_schema = {
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
        validate(instance=data, schema=str_delete_acc_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                               STARTUP INVITE ACCEPT NOTIFICATION SCHEMA
#<==================================================================================================>
str_invite_accepted_notification_schema = {
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
        validate(instance=data, schema=str_invite_accepted_notification_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                                 STARTUP PROFILE VISIBILITY SCHEMA
#<==================================================================================================>
str_profile_vis_schema = {
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
        validate(instance=data, schema= str_profile_vis_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                                STARTUP REMOVE SLIDE DECK SCHEMA
#<==================================================================================================>
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