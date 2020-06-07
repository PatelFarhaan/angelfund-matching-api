import sys
import boto3
import logging
sys.path.append('../')
from common_utilities import CONSTANT
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def wait_list_user(user_email, first_name):
    RECIPIENT = [user_email]
    AWS_REGION = "us-east-1"
    SENDER = "noreply@angelfund.ai"
    AWS_ACCESS_KEY = CONSTANT.ACCESS_KEY.value
    AWS_ACCESS_VALUE = CONSTANT.ACCESS_VALUE.value
    SUBJECT = "WAITLIST"
    BODY_HTML = """
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

</head>
<body style="margin-left: 5%; margin-right: 5%;">
<div>
    <div style="text-align: center;">
        <img src="https://angelfund-profile-pics.s3-us-west-1.amazonaws.com/new_header2.png" style="height: 34px; width: 180px;" />
    </div>
    <br><br>
    <div style="border-bottom: 2px solid #E6E6E6E6;">
        <p style="font-family: Lato; font-weight:700; font-size: 30px; color: #707070;">
        <h1> {first_name} WAIT LIST </h1>
        </p>
    </div>
</div>

</body>
</html>
                """.format(first_name=first_name)
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
        logger.error(f"common utilities: wait list: failed {user_email}")
    else:
        logger.debug(f"common utilities: wait list: success {user_email}")