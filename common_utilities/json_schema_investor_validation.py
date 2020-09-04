#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
from jsonschema import validate
from jsonschema.exceptions import SchemaError
from jsonschema.exceptions import ValidationError


#<==================================================================================================>
#                                 INVESTOR FIRST PAGE SCHEMA
#<==================================================================================================>
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                                     INVESTOR LOGIN SCHEMA
#<==================================================================================================>
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                                  INVESTOR PASSWORD RESET SCHEMA
#<==================================================================================================>
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                                 INVESTOR EMAIL SCHEMA
#<==================================================================================================>
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                                 INVESTOR EMAIL SCHEMA
#<==================================================================================================>
invite_code_schema = {
    "type": "object",
    "properties": {
        "invite_code": {
            "type": "string",
        }
    },
    "required": ["invite_code"],
    "additionalProperties": False
}

def validate_invite_code_schema(data):
    try:
        validate(instance=data, schema= invite_code_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                                    INVESTOR GOOGLE SCHEMA
#<==================================================================================================>
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


#<==================================================================================================>
#                                     INVESTOR DASHBOARD SCHEMA
#<==================================================================================================>
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


#<==================================================================================================>
#                                   INVESTOR REFERRAL SCHEMA
#<==================================================================================================>
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


#<==================================================================================================>
#                                   INVESTOR COMPANY SCHEMA
#<==================================================================================================>
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
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                                 INVESTOR PASSED REVISIT SCHEMA
#<==================================================================================================>
inv_passed_recvisit_schema = {
    "type": "object",
    "properties": {
        "user_id": {
            "type": "string",
            "minLength": 24,
            "maxLength": 24
        },
    },
    "required": ["user_id"],
    "additionalProperties": False
}

def validate_inv_passed_recvisit_schema(data):
    try:
        validate(instance=data, schema= inv_passed_recvisit_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}


#<==================================================================================================>
#                                INVESTOR MONDAY NOTIFICATION SCHEMA
#<==================================================================================================>
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


#<==================================================================================================>
#                                INVESTOR DELETE ACCOUNT SCHEMA
#<==================================================================================================>
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



#<==================================================================================================>
#                             INVESTOR DELETE ACCOUNT CONFIRMATION SCHEMA
#<==================================================================================================>
inv_delete_acc_conf_schema = {
    "type": "object",
    "properties": {
        "delete": {
            "type": "boolean",
        },
    },
    "required": ["delete"],
    "additionalProperties": False
}

def validate_delete_acc_conf_schema(data):
    try:
        validate(instance=data, schema= inv_delete_acc_conf_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}

#<==================================================================================================>
#                             INVESTOR INVITE ACCEPTED NOTIFICATION SCHEMA
#<==================================================================================================>
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


#<==================================================================================================>
#                                   INVESTOR PROFILE VISIT SCHEMA
#<==================================================================================================>
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


#<==================================================================================================>
#                                      ANGEL FUND NAME SCHEMA
#<==================================================================================================>
inv_angel_group_name_schema = {
    "type": "object",
    "properties": {
        "angel_group_name": {
            "type": "string",
        },
    },
    "required": ["angel_group_name"],
    "additionalProperties": False
}

def validate_inv_angel_group_name_schema(data):
    try:
        validate(instance=data, schema= inv_angel_group_name_schema)
    except ValidationError as e:
        return {'result': False, 'error': e.message}
    except SchemaError as e:
        return {'result': False, 'error': e.message}
    return {'result': True, 'data': data}