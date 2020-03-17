import json
import requests

import sys
sys.path.append('../')
from common_utilities import CONSTANT


def redis_get_data(key):
    payload = {"key": key}
    headers = {
      'x-auth-key': CONSTANT.REDIS_CLUSTER_X_AUTH_KEY.value,
      'redis-operations': 'get',
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", CONSTANT.REDIS_CLUSTER_URL.value, headers=headers, data=json.dumps(payload))
    return response.json()


def redis_set_data(key, value):
    payload = {"key": key,
               "value": value
    }
    headers = {
      'x-auth-key': CONSTANT.REDIS_CLUSTER_X_AUTH_KEY.value,
      'redis-operations': 'set',
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", CONSTANT.REDIS_CLUSTER_URL.value, headers=headers, data=json.dumps(payload))
    return response.json()


def redis_key_delete(key):
    payload = {"key": key}
    headers = {
      'x-auth-key': CONSTANT.REDIS_CLUSTER_X_AUTH_KEY.value,
      'redis-operations': 'delete',
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", CONSTANT.REDIS_CLUSTER_URL.value, headers=headers, data=json.dumps(payload))
    return response.json()


def redis_all_keys():
    payload = {}
    headers = {
      'x-auth-key': CONSTANT.REDIS_CLUSTER_X_AUTH_KEY.value,
      'redis-operations': 'keys',
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", CONSTANT.REDIS_CLUSTER_URL.value, headers=headers, data=json.dumps(payload))
    return response.json()


def redis_all_keys_delete():
    payload = {}
    headers = {
      'x-auth-key': CONSTANT.REDIS_CLUSTER_X_AUTH_KEY.value,
      'redis-operations': 'delete_all',
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", CONSTANT.REDIS_CLUSTER_URL.value, headers=headers, data=json.dumps(payload))
    return response.json()