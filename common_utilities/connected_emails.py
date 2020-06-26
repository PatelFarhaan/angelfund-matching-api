import sys
import boto3
import logging
sys.path.append('../')
from common_utilities import CONSTANT
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def email_connected(inv_email: str, str_email: str, all_info):
    RECIPIENT = [inv_email, str_email]
    AWS_REGION = "us-east-1"
    SENDER = "noreply@angelfund.ai"
    AWS_ACCESS_KEY = CONSTANT.ACCESS_KEY.value
    AWS_ACCESS_VALUE = CONSTANT.ACCESS_VALUE.value
    SUBJECT = "A New Connection"
    BODY_HTML = """
  
                """.format(inv_fn=all_info['inv_fn'], str_founders=all_info['str_founders'], str_fn=all_info['str_fn'], str_bio=all_info['str_bio'], inv_bio=all_info['inv_bio'], str_position=all_info['str_position'], str_raised=all_info['str_raised'], str_seeking=all_info['str_seeking'], inv_deals=all_info['inv_deals'])
    CHARSET = "UTF-8"
    client = boto3.client('ses',
                          region_name=AWS_REGION,
                          aws_access_key_id=AWS_ACCESS_KEY,
                          aws_secret_access_key=AWS_ACCESS_VALUE
                          )
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': RECIPIENT,
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        logger.error(f"common utilities: email connected: failed {inv_email, str_email}")
    else:
        logger.debug(f"common utilities: email connected: success {inv_email, str_email}")