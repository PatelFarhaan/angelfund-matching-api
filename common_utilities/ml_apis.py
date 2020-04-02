import sys
import json
import requests
sys.path.append('../')
from common_utilities import CONSTANT


url = CONSTANT.ML_SERVER_EIP.value
content_type = "application/json"
x_auth_key = CONSTANT.ML_SERVER_X_AUTH_KEY.value


def get_discover(url, user_id):
    url = f"{url}get_discover"
    payload = {"user_id": user_id}
    headers = {
      'x-auth-key': x_auth_key,
      'Content-Type': content_type
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


def set_response(url, user_id: int, user_id_to: int, response: bool):
    url = f"{url}set_response"
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


def clean_discover(url):
    url = f"{url}clean_discover"
    payload = {}
    headers = {
        'x-auth-key': x_auth_key,
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


def reset_settings(url, user_id):
    url = f"{url}reset_settings"
    payload = {"user_id": user_id}
    headers = {
        'x-auth-key': x_auth_key,
        'Content-Type': content_type
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


def hide_profile_from_discover(url, user_id):
    url = f"{url}hide_profile_from_discover"
    payload = {"user_id": user_id}
    headers = {
        'x-auth-key': x_auth_key,
        'Content-Type': content_type
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


def delete_user_ml(url, user_id):
    url = f"{url}delete_user"
    payload = {"user_id": user_id}
    headers = {
        'x-auth-key': x_auth_key,
        'Content-Type': content_type
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


resp = get_discover(url, 100400)
print(resp)