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
        <p style="font-family: Lato; font-weight:700; font-size: 30px; color: #707070;">Referral From {full_name}
        </p>
    </div>


    <div style="padding-top: 3%; text-align: center;
             padding-bottom: 3%;border-bottom: 2px solid  #E6E6E6;margin-bottom: 5%;">
        <p style="margin-bottom: 6%;
                padding: 1%;
                margin: 1%;
                font-weight: 700;
                font-family: Roboto;
                font-size: 22px;
                text-align: left;">
            <span>{first_name} is inviting you to join <a style="text-decoration: none;" target="_blank" href="https://www.angelfund.ai"><span style="color: #5a51f4">Angelfund.ai!</span></a></span>
            <br>
            <br>
            <span style="font-weight: 400">
            Sign up using their link to get early access to the most relevant startups & investors:
            <br>
            <br>
        <a href="http://www.angelfund.ai">https://www.angelfund.ai</a>
                </span>

        </p>

        <br>
    </div>
    <div>

    </div>
    <br>
    <div style="font-family: Roboto;
             font-size: 14px;
             color: #919191;
             text-align: center;
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