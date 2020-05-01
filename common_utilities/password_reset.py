import sys
import boto3
import logging
sys.path.append('../')
from common_utilities import CONSTANT
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def password_reset_email(user_email, password_reset_link):
    RECIPIENT = [user_email]
    AWS_REGION = "us-east-1"
    SENDER = "noreply@angelfund.ai"
    AWS_ACCESS_KEY = CONSTANT.ACCESS_KEY.value
    AWS_ACCESS_VALUE = CONSTANT.ACCESS_VALUE.value
    SUBJECT = "Password reset link for your ANGELFUND account"
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
        <p style="font-weight:500;font-size: 30px; color: #7d7676;">Reset Password</p>
    </div>
    <div style="padding-top: 3%;
        padding-bottom: 3%;border-bottom: 3px solid lightgray;margin-bottom: 5%;">
        <strong style="font-weight: 400;font-size: 20px;">
            Resetting your password is simple-we'll have you up and running in no time.
        </strong>
        <p style="margin-bottom: 6%;">
            If you requested a password reset, click here to create a new one:
        </p>
        <div style="text-align: center;">
            <button style="height: 40px;
            background-color: #5a61eb;
            color: white;
            font-size: 16px;
            border-radius: 8px;"><a style="color:white; text-decoration: none;" target="_blank"
                    href="{password_reset_link}">Reset my Password</a></button>
        </div>
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
    """.format(password_reset_link=password_reset_link)
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