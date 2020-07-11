#<==================================================================================================>
#                                      IMPORTS
#<==================================================================================================>
import sys
import json
import requests
sys.path.append('../')
from common_utilities import CONSTANT


#<==================================================================================================>
#                                      CONFIG
#<==================================================================================================>
content_type = "application/json"
x_auth_key = CONSTANT.ML_SERVER_X_AUTH_KEY.value


#<==================================================================================================>
#                                      GET DISCOVER
#<==================================================================================================>
def get_discover(user_id):
    url = f"{CONSTANT.ML_SERVER_EIP.value}get_discover"
    payload = {"user_id": user_id}
    headers = {
      'x-auth-key': x_auth_key,
      'Content-Type': content_type
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


#<==================================================================================================>
#                                     SET RESPONSES
#<==================================================================================================>
def set_response(user_id: int, user_id_to: int, response: bool):
    url = f"{CONSTANT.ML_SERVER_EIP.value}set_response"
    payload = {
        "user_id": user_id,
        "user_id_to": user_id_to,
        "response": response
    }
    headers = {
        'x-auth-key': x_auth_key,
        'Content-Type': content_type
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


#<==================================================================================================>
#                                    RESET SETTINGS
#<==================================================================================================>
def reset_settings(user_id):
    url = f"{CONSTANT.ML_SERVER_EIP.value}reset_settings"
    payload = {"user_id": user_id}
    headers = {
        'x-auth-key': x_auth_key,
        'Content-Type': content_type
    }
    try:
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    except:
        return False
    return True


#<==================================================================================================>
#                               HIDE PROFILE FROM DISCOVER
#<==================================================================================================>
def hide_profile_from_discover(user_id):
    url = f"{CONSTANT.ML_SERVER_EIP.value}hide_profile_from_discover"
    payload = {"user_id": user_id}
    headers = {
        'x-auth-key': x_auth_key,
        'Content-Type': content_type
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


#<==================================================================================================>
#                                 DELETE USER FROM ML
#<==================================================================================================>
def delete_user_ml(user_id):
    url = f"{CONSTANT.ML_SERVER_EIP.value}delete_user"
    payload = {"user_id": user_id}
    headers = {
        'x-auth-key': x_auth_key,
        'Content-Type': content_type
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()