#<==================================================================================================>
#                                       IMPORTS
#<==================================================================================================>
import sys
import boto3
import string
import logging
sys.path.append('../../')
from common_utilities import CONSTANT
from botocore.exceptions import ClientError


#<==================================================================================================>
#                                       LOGGER
#<==================================================================================================>
logger = logging.getLogger(__name__)


#<==================================================================================================>
#                                   EMAIL REFERRAL
#<==================================================================================================>
def email_referral(user_email, full_name, first_name, link, is_investor, domain):
    RECIPIENT = [user_email]
    first_name = first_name.capitalize()
    full_name = string.capwords(full_name)
    AWS_REGION = CONSTANT.EMAIL_REGION.value
    SENDER = "Angelfund.ai <hello@angelfund.ai>"
    AWS_ACCESS_KEY = CONSTANT.ACCESS_KEY.value
    AWS_ACCESS_VALUE = CONSTANT.ACCESS_VALUE.value
    SUBJECT = f"{first_name} has invited you to join Angelfund.ai!"
    BODY_HTML = f"""
<html>
   <head>
      <link
         rel="stylesheet"
         href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
         />
      <style>
         body,
         html {{
         margin: 0 !important;
         padding: 0 !important;
         }}
         .container {{
         display: block !important;
         width: 600px !important;
         margin: auto !important;
         font-family: "Roboto", sans-serif !important;
         border: 2px solid #f3f3f3 !important;
         box-shadow: 0px 2px 3px 0px #f2f2ff !important;
         margin-top: 5% !important;
         border-radius: 5px !important;
         }}
         p,
         h1,
         .sizing {{
         font-family: "Roboto", sans-serif !important;
         }}
         p {{
         margin: 30px 0 !important;
         }}
         .logo {{
         display: block !important;
         margin: auto !important;
         text-align: center !important;
         padding-top: 10px !important;
         }}
         .title {{
         padding-top: 30px;
         padding-bottom: 10px;
         padding-left: 10px;
         border-bottom: 2px solid #e6e6e6;
         }}
         .hook {{
         padding-top: 30px;
         text-align: left;
         padding-bottom: 10px;
         margin: 3%;
         }}
         .footer {{
         margin: 0% !important;
         left: 0%;
         bottom: 0%;
         width: 100%;
         text-align: center;
         background-color: lightgrey;
         opacity: 0.3;
         padding: 2% 0;
         }}
         h1 {{
         font-size: 28px !important;
         font-family: Lato;
         font-weight: 500;
         color: #707070;
         }}
         strong {{
         font-weight: 500;
         }}
         .sizing {{
         font-size: 17px !important;
         }}
         a {{
         transition: all 0.5s ease-in-out;
         }}
         a:hover {{
         font-size: 18px;
         }}
         @media only screen and (max-width: 600px) {{
         .logo {{
         padding-left: 5%;
         margin: 0px !important;
         text-align: left !important;
         }}
         .container {{
         margin: 0px !important;
         padding: 0% !important;
         border: none !important;
         box-shadow: none !important;
         width: 100% !important;
         }}
         .hook {{
         display: block;
         margin: auto;
         width: 80%;
         }}
         h1 {{
         font-size: 20px !important;
         }}
         .sizing {{
         font-size: 15px !important;
         }}
         .title {{
         padding-left: 5% !important;
         margin-left: 0% !important;
         }}
         }}
      </style>
   </head>
   <div class="container">
      <div class="logo">
         <img
            src="https://angelfund-company-images.s3-us-west-1.amazonaws.com/Icons/Angelfund.ai+Logo.png"
            style="height: 30px; width: 165px;"
            />
      </div>
      <div class="title">
         <h1>
            Referral From {full_name}
         </h1>
      </div>
      <div class="hook">
         <strong class="sizing">
         {first_name} is inviting you to join
         <span style="color: #5e51f4;">Angelfund.ai!</span>
         </strong>
         <p class="sizing">
            Sign up using their link to get early access to the most relevant
            startups & investors:
         </p>
         <p class="sizing" style="text-decoration: none;">
            <a
               style="
               word-wrap: break-word;
               text-decoration: underline;
               color: #5e51f4;
               "
               href="{link}"
               >{domain}/api/v1/{is_investor}/referral/{first_name}</a
               >
         </p>
      </div>
      <div class="footer">
         <div>
            <a target="_blank" href="https://twitter.com/angelfundAI">
            <img src="https://angelfund-company-images.s3-us-west-1.amazonaws.com/twitter-512.png" style="
               height: 25px;
               width: 25px;
               text-decoration: none;
               margin-right: 10px;
               color: gray; 
               "></img>
            </a>
            <a target="_blank" href="https://www.linkedin.com/company/angelfundai">
            <img src="https://angelfund-company-images.s3-us-west-1.amazonaws.com/25325.png" style="
               height: 25px;
               width: 25px;
               text-decoration: none;
               color: gray;
               "></img>
            </a>
         </div>
         <p>
            2375 Zanker Road #250, San Jose, CA 95131
         </p>
         <footer>
            Copyright &copy;2020 Global Angel Fund, Inc.
         </footer>
      </div>
   </div>
</html>
"""
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