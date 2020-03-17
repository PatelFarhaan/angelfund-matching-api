import sys
sys.path.append('../')
from common_utilities import CONSTANT

import json
import requests


def company_image(company_name):
    x_auth_key = CONSTANT.COMPANY_IMAGES_X_AUTH_KEY.value
    url = CONSTANT.COMPANY_IMAGES_URL.value
    payload = {"company_name": company_name}
    headers = {
      'x-auth-key': x_auth_key,
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()