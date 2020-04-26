import sys
import json
import requests
sys.path.append('../')
from common_utilities import CONSTANT


content_type = "application/json"
x_auth_key = CONSTANT.ML_SERVER_X_AUTH_KEY.value



def get_discover(user_id):
    url = f"{CONSTANT.ML_SERVER_EIP.value}get_discover"
    payload = {"user_id": user_id}
    headers = {
      'x-auth-key': x_auth_key,
      'Content-Type': content_type
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


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


def clean_discover():
    url = f"{CONSTANT.ML_SERVER_EIP.value}clean_discover"
    payload = {}
    headers = {
        'x-auth-key': x_auth_key,
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


def reset_settings(user_id):
    url = f"{CONSTANT.ML_SERVER_EIP.value}reset_settings"
    payload = {"user_id": user_id}
    headers = {
        'x-auth-key': x_auth_key,
        'Content-Type': content_type
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


def hide_profile_from_discover(user_id):
    url = f"{CONSTANT.ML_SERVER_EIP.value}hide_profile_from_discover"
    payload = {"user_id": user_id}
    headers = {
        'x-auth-key': x_auth_key,
        'Content-Type': content_type
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


def delete_user_ml(user_id):
    url = f"{CONSTANT.ML_SERVER_EIP.value}delete_user"
    payload = {"user_id": user_id}
    headers = {
        'x-auth-key': x_auth_key,
        'Content-Type': content_type
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()