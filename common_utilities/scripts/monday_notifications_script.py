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
    remote_mongo_uri = CONSTANT.TEST_DB_CLUSTER.value
    mongo_client = MongoClient(remote_mongo_uri)
    db = mongo_client.matching
    collection = db.users

    my_query = {"monday_notification": True}

    total_count = collection.estimated_document_count()
    for offset in range(0, total_count, 100):
        data_chunk = list(collection.find(my_query).skip(offset).limit(100))

        for doc in data_chunk:
            email = doc.get("email")
            last_name = doc.get("last_name")
            first_name = doc.get("first_name")
            if email in ("patel.farhaaan@gmail.com"):
                thread = threading.Thread(target=wait_list_user, args=(email, first_name))
                thread.start()
                time.sleep(0.01)
                wait_list_user(email, first_name)


#<==================================================================================================>
#                                MONDAY NOTIFICATIONS EMAIL
#<==================================================================================================>
def wait_list_user(user_email, first_name):
    RECIPIENT = [user_email]
    AWS_REGION = "us-east-1"
    SENDER = "noreply@angelfund.ai"
    AWS_ACCESS_KEY = CONSTANT.ACCESS_KEY.value
    AWS_ACCESS_VALUE = CONSTANT.ACCESS_VALUE.value
    SUBJECT = "MONDAY NOTIFICATIONS"
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
        <p style="font-family: Lato; font-weight:700; font-size: 30px; color: #707070;">
        <h1> {first_name}, Monday Email Notifications </h1>
        </p>
    </div>
</div>

</body>
</html>
                """.format(first_name=first_name)
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
