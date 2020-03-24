import sys
sys.path.append('../')
from common_utilities import CONSTANT

import json
import logging
import requests

logger = logging.getLogger(__name__)

def company_image(company_name):
    x_auth_key = CONSTANT.COMPANY_IMAGES_X_AUTH_KEY.value
    url = CONSTANT.COMPANY_IMAGES_URL.value
    payload = {"company_name": company_name}
    headers = {
      'x-auth-key': x_auth_key,
      'Content-Type': 'application/json'
    }
    logger.debug(f"common utilities: company images: {company_name}")
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()