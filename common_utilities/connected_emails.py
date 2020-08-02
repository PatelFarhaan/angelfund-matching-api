#<==================================================================================================>
#                                         IMPORTS
#<==================================================================================================>
import sys
import boto3
import logging
sys.path.append('../')
from common_utilities import CONSTANT
from botocore.exceptions import ClientError


#<==================================================================================================>
#                                         LOGGER
#<==================================================================================================>
logger = logging.getLogger(__name__)


#<==================================================================================================>
#                                    EMAILS CONNECTED
#<==================================================================================================>
def email_connected(inv_email: str, str_email: str, all_info):
    RECIPIENT = [inv_email, str_email]
    SENDER = CONSTANT.EMAIL_SENDER.value
    AWS_REGION = CONSTANT.EMAIL_REGION.value
    AWS_ACCESS_KEY = CONSTANT.ACCESS_KEY.value
    AWS_ACCESS_VALUE = CONSTANT.ACCESS_VALUE.value
    SUBJECT = f"Angelfund.ai Intro: {all_info['inv_fn']} – {all_info['str_founders']}"
    BODY_HTML = """
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
         width: 100% !important;
         margin: auto !important;
         font-family: "Roboto", sans-serif !important;
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
         .hook {{
         padding-top: 30px;
         text-align: left;
         padding-bottom: 10px;
         margin: 3%;
         }}
         h1 {{
         font-size: 28px !important;
         font-family: Lato;
         font-weight: 500;
         color: #707070;
         }}
         strong {{
         font-weight: 600;
         }}
         .sizing {{
         font-size: 17px !important;
         }}
         @media only screen and (max-width: 600px) {{
         .container {{
         margin: 0px !important;
         padding: 0% !important;
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
         }}
      </style>
   </head>
   <div class="container">
      <div class="hook">
         <strong class="sizing"> {inv_fn}—meet {str_fn} from {str_cn}. </strong>
         <p class="sizing">
            <span style="font-style: italic;"> Quick synopsis on {str_fn}:</span
               ><br />
            {str_pitch}<br />They’re currently raising a ${str_seeking:,} round and would like
            to coordinate a time to share more about the opportunity.
         </p>
         <br />
         <strong class="sizing"> {str_founders}—meet {inv_fn}. </strong>
         <p class="sizing">
            {inv_fn} invests in companies within your sector, and is interested in
            learning more about {str_fn}.
         </p>
         <br />
         <p class="sizing">
            We’ll let you two take it from here.
         </p>
         <p class="sizing">
            Best,<br />
            Angelfund.ai
         </p>
      </div>
   </div>
</html>
    """.format(inv_fn=all_info['inv_fn'], str_founders=all_info['str_founders'],
               str_pitch=all_info['str_pitch'], str_cn=all_info['str_cn'],
               str_fn=all_info['str_fn'], str_bio=all_info['str_bio'],
               str_seeking=int(all_info['str_seeking']))
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