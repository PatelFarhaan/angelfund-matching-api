import sys
import json
import logging
import requests
sys.path.append('../')
from common_utilities import CONSTANT


logger = logging.getLogger(__name__)


def failed_company_image_email(company_name):
    x_auth_key = CONSTANT.FAILED_IMAGES_X_AUTH_KEY.value
    url = CONSTANT.FAILED_IMAGES_URL.value
    payload = {"company_name": company_name}
    headers = {
      'x-auth-key': x_auth_key,
      'Content-Type': 'application/json'
    }
    logger.debug(f"common utilities: failed company images: {company_name}")
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.json()