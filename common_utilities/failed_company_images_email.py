import json
import requests

import sys
sys.path.append('../')
from common_utilities import CONSTANT


def failed_company_image_email(company_name):
    x_auth_key = CONSTANT.FAILED_IMAGES_X_AUTH_KEY.value
    url = "https://u6lzj60oy6.execute-api.us-west-1.amazonaws.com/dev/v1/angelfund/failed_company_images_email"
    payload = {"company_name": company_name}
    headers = {
      'x-auth-key': x_auth_key,
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()