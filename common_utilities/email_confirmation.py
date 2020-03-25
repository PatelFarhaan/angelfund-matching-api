import sys
import boto3
import logging
sys.path.append('../')
from common_utilities import CONSTANT
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def email_confirmation(user_email, email_confirm_link):
    RECIPIENT = [user_email]
    AWS_REGION = "us-east-1"
    SENDER = "noreply@angelfund.ai"
    AWS_ACCESS_KEY = CONSTANT.ACCESS_KEY.value
    AWS_ACCESS_VALUE = CONSTANT.ACCESS_VALUE.value
    SUBJECT = "Please confirm your email address for ANGELFUND"
    BODY_TEXT = ("Please click the following link to confirm your email address"
                 f"{email_confirm_link}"
                 "By Team,"
                 "ANGELFUND AI."
                 )
    BODY_HTML = """<html>
    <head></head>
    <body>
      <p>Please click the following link to confirm your email address
        <a href='{email_confirm_link}'>Click here</a>.
        <br>
        <br>
        By Team,
        <br>
        ANGELFUND AI.
        </p>
    </body>
    </html>
                """.format(email_confirm_link=email_confirm_link)
    CHARSET = "UTF-8"
    client = boto3.client('ses',
                          region_name=AWS_REGION,
                          aws_access_key_id=AWS_ACCESS_KEY,
                          aws_secret_access_key=AWS_ACCESS_VALUE
                          )
    # try:
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
                'Text': {
                    'Charset': CHARSET,
                    'Data': BODY_TEXT,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            },
        },
        Source=SENDER,
    )
    # except ClientError as e:
    #     logger.error(f"common utilities: email confirmation: failed {user_email}")
    # else:
    #     logger.debug(f"common utilities: email confirmation: success {user_email}")


email_confirmation("patel.farhaaan@gmail.com", "ASd")
