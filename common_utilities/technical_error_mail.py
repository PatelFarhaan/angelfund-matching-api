import sys
import boto3
import logging
sys.path.append('../')
from common_utilities import CONSTANT
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def technical_errors(subject, user_email):
    # RECIPIENT = ["patel.farhaaan@gmail.com", "colby@angelfund.ai", "liya@angelfund.ai"]
    RECIPIENT = ["patel.farhaaan@gmail.com"]
    AWS_REGION = "us-east-1"
    SENDER = "technical_errors@angelfund.ai"
    AWS_ACCESS_KEY = CONSTANT.ACCESS_KEY.value
    AWS_ACCESS_VALUE = CONSTANT.ACCESS_VALUE.value
    SUBJECT = f"{subject}: {user_email}"
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

</body>
</html>
                """.format()
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
        logger.error(f"common utilities: technical errors: failed {user_email}")
    else:
        logger.debug(f"common utilities: technical errors: success {user_email}")