import boto3

import sys
sys.path.append('../')
from common_utilities import CONSTANT


def file_upload_to_s3(file, object_name):
    bucket = 'angelfund-profile-pics'
    s3 = boto3.client(
        's3',
        aws_access_key_id=CONSTANT.ACCESS_KEY.value,
        aws_secret_access_key=CONSTANT.ACCESS_VALUE.value
    )
    s3.upload_fileobj(file, bucket, object_name, ExtraArgs={"ACL": "public-read"})
    public_url = f"https://{bucket}.s3-us-west-1.amazonaws.com/{object_name}"
    return public_url