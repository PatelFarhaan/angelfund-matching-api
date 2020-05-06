import sys
import boto3
import logging
sys.path.append('../')
from common_utilities import CONSTANT
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def email_referral(user_email, full_name, first_name):
    full_name = full_name.capitalize()
    first_name = first_name.capitalize()
    RECIPIENT = [user_email]
    AWS_REGION = "us-east-1"
    SENDER = "noreply@angelfund.ai"
    AWS_ACCESS_KEY = CONSTANT.ACCESS_KEY.value
    AWS_ACCESS_VALUE = CONSTANT.ACCESS_VALUE.value
    SUBJECT = "Welcome to AngelFund"
    BODY_HTML = """
<HTML>

<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
</head>
<div style="margin-left: 5%;margin-right: 5%;">
    <div style="text-align: center;">
        <img src="https://angelfund-profile-pics.s3-us-west-1.amazonaws.com/angelfund.png" style="height: 110px;" />
    </div>
    <div style="border-bottom: 3px solid lightgray;">
        <p style="font-weight:500;font-size: 30px; color: #7d7676;">Referral From {full_name}</p>
    </div>
    <div style="padding-top: 3%;
            padding-bottom: 3%;border-bottom: 3px solid lightgray;margin-bottom: 5%;">
        <strong style="font-weight: 400; margin-bottom: 3%; font-size: 25px;">
            {first_name} is inviting you to join <span style="color: rgb(66, 66, 255);">AngelFund.ai!</span>
        </strong>
        <p style="margin-bottom: 2%;font-size: 20px;">
            Sign up using their link to get early access to the most relevant startups & investors
        </p>
        <p style="margin-bottom: 6%;font-size: 20px;text-decoration: none;">
            <a style="text-decoration: none;" href="https://www.angelfund.ai">https://www.angelfund.ai</a>

        </p>

    </div>
    <div style="text-align: center;background-color: lightgrey;opacity: 0.3;padding-top: 2%;padding-bottom: 2%;">
        <div>
            <a href="#" class="fa fa-twitter"
                style="font-size: 25px;text-decoration: none;margin-right: 10px;color: gray;"></a>
            <a href="#" class="fa fa-linkedin" style="font-size: 25px;text-decoration: none;color: gray;"></a>
        </div>
        <p>
            2375 Zanker Road #250, San Jose, CA 95131
        </p>
        <footer>Copyright &copy;2020 Global Angel Fund, Inc. <a style="text-decoration: underline;">Unsubscribe</a>
        </footer>
    </div>
</div>

</HTML>
                """.format(full_name=full_name, first_name=first_name)
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
        logger.error(f"common utilities: email confirmation: failed {user_email}")
    else:
        logger.debug(f"common utilities: email confirmation: success {user_email}")