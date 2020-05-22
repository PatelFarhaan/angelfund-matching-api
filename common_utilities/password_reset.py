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
        <p style="font-family: Lato; font-weight:700; font-size: 30px; color: #707070;">Reset Password
        </p>
    </div>


    <div style="padding-top: 3%; text-align: center;
             padding-bottom: 3%;border-bottom: 2px solid  #E6E6E6;margin-bottom: 5%;">
        <p style="margin-bottom: 6%;
                padding: 1%;
                margin: 1%;
                font-weight: 500;
                font-family: Roboto;
                font-size: 20px;
                text-align: center;">
            <span>Resetting your password is simple—we'll have you up and running in no time.</span>
            <br>
            <span style="font-weight: 400;">
            If you requested a password reset, click here to choose a new one:
                </span>
        </p>
        <div style="text-align: center;">
            <a style="color:white; text-decoration: none;" target="_blank"
               href="{password_reset_link}">
                <button style="
                   background-color: #5a51f4;
                   color: white;
                   min-height: 6%;
                   height: auto;
                   border: none;
                   width: 15%;
                   font-weight: 700;
                   font-size: 18px;
                   border-radius: 4px;">Reset my password</button></a>
        </div>
    </div>
    <div>
        <p style="margin-bottom: 6%;
                padding: 1%;
                margin: 1%;
                color: #707070;
                font-weight: 400;
                font-family: Roboto;
                font-size: 18px;
                text-align: left;">
            <strong>Button not working?</strong>
            <br>
            Just click on the link below or paste it into your browser.
            <br>
            <a style="color: #707070;">{password_reset_link}</a>
            <br>
            <br>
            You received this email because you signed up for an Angelfund.ai account with this
            <br>
            email address. If this was a mistake, please ignore this message.
        </p>
    </div>
    <br>
    <br>
    <div style="font-family: Roboto;
             font-size: 14px;
             text-align: center;
             color: #919191;
             background-color: #F8F8F8;
             border-radius: 4px;
             padding-top: 2%;
             padding-bottom: 2%;">
        <div>
            <a href="https://mobile.twitter.com/AngelFundAI" class="fa fa-twitter"
               style="font-size: 25px;text-decoration: none;margin-right: 20px;color: gray;"></a>
            <a href="https://www.linkedin.com/company/angelfundai/" class="fa fa-linkedin"
               style="font-size: 25px; margin-left: 20px; text-decoration: none;color: gray;"></a>
        </div>
        <p>
            2375 Zanker Road #250, San Jose, CA 95131
        </p>
        <footer>Copyright &copy;2020 Global Angel Fund, Inc.
        </footer>
    </div>
</div>
</body>

</html>
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