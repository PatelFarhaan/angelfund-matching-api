#<==================================================================================================>
#                                        IMPORTS
#<==================================================================================================>
import sys
import boto3
import logging
sys.path.append('../')
from common_utilities import CONSTANT
from botocore.exceptions import ClientError


#<==================================================================================================>
#                                        LOGGER
#<==================================================================================================>
logger = logging.getLogger(__name__)


#<==================================================================================================>
#                                 RESET PASSWORD EMAIL TEMPLATE
#<==================================================================================================>
def password_reset_email(user_email, password_reset_link):
    """
    Sending the user an email to reset their passowrd

    :parameter
      ==> user_email          :str
      ==> password_reset_link :str

    :returns
      ==> None                :None

    """
    RECIPIENT = [user_email]
    AWS_REGION = "us-east-1"
    SENDER = "noreply@angelfund.ai"
    AWS_ACCESS_KEY = CONSTANT.ACCESS_KEY.value
    AWS_ACCESS_VALUE = CONSTANT.ACCESS_VALUE.value
    SUBJECT = "Reset your Angelfund.ai password"
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
        width: 600px !important;
        margin: auto !important;
        font-family: "Roboto", sans-serif !important;
        border: 2px solid #f3f3f3 !important;
        box-shadow: 0px 2px 3px 0px #f2f2ff !important;
        margin-top: 2% !important;
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
        text-align: center;
        padding-bottom: 10px;
        margin: 3%;
      }}

      .bottom-text {{
        margin: 3%;
        padding-bottom: 10px;
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

      button {{
        height: 50px;
        margin-top: 10px;
        /* margin-left: 15%; */
        padding: 10px 30px;
        background-color: #5e51f4;
        color: white;
        font-size: 16px;
        font-weight: bold;
        border-radius: 5px;
        box-shadow: none;
        border: none;
        transition: all 0.5s ease-in-out;
      }}

      button:hover {{
        transform: scale(1.1);
      }}

      .bottom-section {{
        text-align: left !important;
        color: #707070 !important;
        border-top: 2px solid #e6e6e6;
        margin-top: 35px;
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

        .footer {{
          font-size: 15px;
        }}

        button {{
          margin-left: 0px !important;
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
      <h1>Reset Password</h1>
    </div>
    <div class="hook">
      <strong class="sizing">
        Resetting your password is simple-we'll have you up and running in no
        time.
      </strong>
      <p style="margin-bottom: 6%;" class="sizing">
        If you requested a password reset, click here to create a new one:
      </p>
      <div style="text-align: center;">
  <a style="color: white; text-decoration: none;" target="_blank" href="{password_reset_link}">
    <button>
      Reset my Password
    </button>
  </a>
</div>
    </div>
    <div class="bottom-section">
      <div class="bottom-text">
        <p class="sizing">
          <strong class="sizing">Button not working?</strong><br />
          Just click on the link below or paste it into your browser.
          {password_reset_link}
        </p>
        <p class="sizing">
          You received this email because you requested a password reset. If you
          did not,
          <span style="text-decoration: underline;">please contact us.</span>
        </p>
      </div>
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