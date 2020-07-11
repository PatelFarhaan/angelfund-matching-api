#<==================================================================================================>
#                                        IMPORTS
#<==================================================================================================>
import sys
import time
import boto3
import logging
import threading
sys.path.append("../../")
from pymongo import MongoClient
from common_utilities import CONSTANT
from botocore.exceptions import ClientError


#<==================================================================================================>
#                                        LOGGER
#<==================================================================================================>
logger = logging.getLogger(__name__)


#<==================================================================================================>
#                                MONDAY NOTIFICATIONS LOGIC
#<==================================================================================================>
def monday_notofication():
    remote_mongo_uri = CONSTANT.PRIMARY_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.users

    my_query = {"monday_notification": True}

    total_count = collection.estimated_document_count()
    for offset in range(0, total_count, 100):
        data_chunk = list(collection.find(my_query).skip(offset).limit(100))

        for doc in data_chunk:
            email = doc.get("email")
            first_name = doc.get("first_name")
            is_investor = True if doc.get("investor") is True else False
            if is_investor:
                if email in ("patel.farhaaan@gmail.com", "mohammedfarhaan.patel@sjsu.edu"):
                    thread = threading.Thread(target=wait_list_user_investor, args=(email, first_name))
                    thread.start()
                    time.sleep(0.01)
            else:
                if email in ("patel.farhaaan@gmail.com", "mohammedfarhaan.patel@sjsu.edu"):
                    thread = threading.Thread(target=wait_list_user_startup, args=(email, first_name))
                    thread.start()
                    time.sleep(0.01)


#<==================================================================================================>
#                              MONDAY NOTIFICATIONS EMAIL STARTUP
#<==================================================================================================>
def wait_list_user_startup(user_email, first_name):
    RECIPIENT = [user_email]
    AWS_REGION = "us-east-1"
    SENDER = "noreply@angelfund.ai"
    AWS_ACCESS_KEY = CONSTANT.ACCESS_KEY.value
    AWS_ACCESS_VALUE = CONSTANT.ACCESS_VALUE.value
    SUBJECT = f"{first_name}, new investors are waiting for you! :stopwatch:"
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
        width: 700px !important;
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
        padding-top: 5px;
        text-align: left;
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
        width: 700px;
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
        margin-top: 30px;
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

      @media only screen and (max-width: 700px) {{
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

        .bottom-section {{
          margin: auto;
        }}

        .bottom-text {{
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
          text-align: center;
          width: 100%;
        }}

        button {{
          margin-left: 0px !important;
          margin-bottom: 30px !important;
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
      <h1>{first_name}, new investors are waiting for you! ⏱️</h1>
    </div>
    <div class="hook">
      <p class="sizing">
        Hey {first_name}—
      </p>
      <p class="sizing">
        You've got new investors waiting for you on Angelfund.ai!
      </p>
      <p class="sizing">
        Every week, our algorithm learns more about your preferences and gets
        better at finding you the most relevant investors.
      </p>
      <strong style="margin-bottom: 6%;" class="sizing">
        That means every week, Angelfund.ai will show you better investors.
      </strong>
      <div style="text-align: left;">
        <button target="_blank" href="https://www.angelfund.ai/login">
          <a style="color: white; text-decoration: none;"
            >See This Week's Investors</a
          >
        </button>
      </div>
    </div>
    <div class="bottom-section">
      <div class="bottom-text">
        <p class="sizing">
          <strong class="sizing">Button not working?</strong><br />
          Just click on the link below or paste it into your browser.
          https://www.angelfund.ai/login
        </p>
        <p class="sizing">
          You received this email because you requested to be alerted when there
          are new deals. If you did not,
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
                """.format(first_name=first_name, dashboard_link=None)
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
        logger.error(f"common utilities: monday notifications: failed {user_email}")
    else:
        logger.debug(f"common utilities: monday notifications: success {user_email}")



#<==================================================================================================>
#                              MONDAY NOTIFICATIONS EMAIL INVESTOR
#<==================================================================================================>
def wait_list_user_investor(user_email, first_name):
    RECIPIENT = [user_email]
    AWS_REGION = "us-east-1"
    SENDER = "noreply@angelfund.ai"
    AWS_ACCESS_KEY = CONSTANT.ACCESS_KEY.value
    AWS_ACCESS_VALUE = CONSTANT.ACCESS_VALUE.value
    SUBJECT = f"{first_name}, new startups are waiting for you! :stopwatch:"
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
        width: 700px !important;
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
        padding-top: 5px;
        text-align: left;
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
        width: 700px;
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
        margin-top: 30px;
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

      @media only screen and (max-width: 700px) {{
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

        .bottom-section {{
          margin: auto;
        }}

        .bottom-text {{
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
          text-align: center;
          width: 100%;
        }}

        button {{
          margin-left: 0px !important;
          margin-bottom: 30px !important;
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
      <h1>{first_name}, new startups are waiting for you! ⏱️</h1>
    </div>
    <div class="hook">
      <p class="sizing">
        Hey {first_name}—
      </p>
      <p class="sizing">
        You've got new deals waiting for you on Angelfund.ai!
      </p>
      <p class="sizing">
        Every week, our algorithm learns more about your preferences and gets
        better at finding you the most relevant startups.
      </p>
      <strong style="margin-bottom: 6%;" class="sizing">
        That means every week, Angelfund.ai will show you better deals.
      </strong>
      <div style="text-align: left;">
        <button target="_blank" href="https://www.angelfund.ai/login">
          <a style="color: white; text-decoration: none;"
            >See This Week's Deals</a
          >
        </button>
      </div>
    </div>
    <div class="bottom-section">
      <div class="bottom-text">
        <p class="sizing">
          <strong class="sizing">Button not working?</strong><br />
          Just click on the link below or paste it into your browser.
          https://www.angelfund.ai/login
        </p>
        <p class="sizing">
          You received this email because you requested to be alerted when there
          are new deals. If you did not,
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
                """.format(first_name=first_name, dashboard_link=None)
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
        logger.error(f"common utilities: monday notifications: failed {user_email}")
    else:
        logger.debug(f"common utilities: monday notifications: success {user_email}")


#<==================================================================================================>
#                             MONDAY NOTIFICATIONS CALLING FUNCTION
#<==================================================================================================>
monday_notofication()


# * * * * * cd /Users/farhaan/projects && source venv/bin/activate && cd /Users/farhaan/projects/angelfund/flask/common_utilities/scripts && python3 monday_notifications_script.py
