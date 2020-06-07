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
   <HTML>
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
  
     <style>
        .display_div {{
            display: flex;
            margin-top: 5%;
            margin-bottom: 5%;
        }}

        .padding_div {{
            padding-left: 4%;
            padding-right: 4%;
        }}

        .angel_fund {{
            margin-top: 5%;
            margin-bottom: 5%;
        }}

        .col-lg-4 {{

            flex: 0 0 33.333333%;
            max-width: 33.333333%;
        }}

        .col-md-4 {{

            flex: 0 0 33.333333%;
            max-width: 33.333333%;
        }}

        .rounded {{
            border-radius: .25rem !important;
        }}

        .rounded-circle {{
            border-radius: 50% !important;
        }}

        .col-lg-6 {{

            flex: 0 0 40%;
            max-width: 40%;
        }}

        .col-md-6 {{

            flex: 0 0 40%;
            max-width: 40%;
        }}
    </style>
</head>
<div style="margin-left: 5%;margin-right: 5%;">
    <div class="angel_fund" style="text-align: center;">
        <img src="https://angelfund-profile-pics.s3-us-west-1.amazonaws.com/angelfund.png" style="height: 110px;" />
    </div>

    <div style="text-align: center;">
        <div class="col-md-4 col-lg-4"
            style="margin: auto;box-shadow: 0 0px 0px 0 rgba(0, 0, 0, 0.2), 0 0px 16px 0 rgba(0, 0, 0, 0.19);">

            <div class="rounded" style="padding: 5%;">
                <img width="150px" height="150px" class="rounded-circle" src="{inv_img}">
                <img width="150px" height="150px" class="rounded-circle" src="{str_img}">
            </div>

        </div>
    </div>
    <div class="display_div">
        <div class="padding_div col-md-6 col-lg-6" style="border-right: 1px solid lightgrey;">
            <div style="padding-top:7% ;">
                <p>
                    {inv_fn}, meet {str_founders} from {str_fn}.
                </p>
                <p style="font-weight: 400;font-size: 25px;">
                    {str_bio}
                </p>
                <p style="font-weight: 400;font-size: 20px;">
                    {str_founders} is the {str_position} at {str_fn}, which has raised{str_raised} out of a seeking
                    of {str_seeking} round.
                </p>
            </div>
        </div>
        <div class="padding_div col-md-6 col-lg-6">
            <div style="padding-top:7% ;"></div>
            <p>
                {str_founders}, meet {inv_fn}.
            </p>
            <p style="font-weight: 400;font-size: 25px;">
                {inv_bio}.
            </p>
            <p style="font-weight: 400;font-size: 20px;">
                {inv_fn} is interested in investing in the {inv_deals} range.
            </p>
        </div>
    </div>
    <div style="text-align: center;">

        <p>
            Reply to this thread to set up a virtual meeting via Zoom, Hangouts, phone call, or whatever works for you.

        </p>
        <p>
            We’re glad you’re connected!

        </p>
        <p>
            Sincerely,


        </p>
        <p>
            The Angelfund.ai Team

        </p>

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
                """.format(inv_img=all_info['inv_img'], str_img=all_info['str_img'], inv_fn=all_info['inv_fn'], str_founders=all_info['str_founders'], str_fn=all_info['str_fn'], str_bio=all_info['str_bio'], inv_bio=all_info['inv_bio'], str_position=all_info['str_position'], str_raised=all_info['str_raised'], str_seeking=all_info['str_seeking'], inv_deals=all_info['inv_deals'])
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