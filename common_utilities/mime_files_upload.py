#<==================================================================================================>
#                                      IMPORTS
#<==================================================================================================>
import sys
import boto3
sys.path.append("../")
from common_utilities import CONSTANT


#<==================================================================================================>
#                               PROFILE PIC UPLOAD TO S3
#<==================================================================================================>
def profile_pic_upload_to_s3(object_name, extention, file_location, file_obj_name):
    bucket = 'angelfund-profile-pics'
    s3_client = boto3.client('s3',
                             aws_access_key_id=CONSTANT.ACCESS_KEY.value,
                             aws_secret_access_key=CONSTANT.ACCESS_VALUE.value
                             )
    object_name = f"{object_name}.{extention}"
    s3_client.upload_file(f"{file_location}/{file_obj_name}", bucket, object_name,
                          ExtraArgs={'ACL': 'public-read'})
    public_url = f'https://{bucket}.s3-us-west-1.amazonaws.com/{object_name}'
    return public_url


#<==================================================================================================>
#                                  PDF UPLOAD TO S3
#<==================================================================================================>
def pdf_upload_to_s3(object_name, extention, file_location, file_obj_name):
    bucket = 'angelfund-client-pdf-bucket'
    s3_client = boto3.client('s3',
                             aws_access_key_id=CONSTANT.ACCESS_KEY.value,
                             aws_secret_access_key=CONSTANT.ACCESS_VALUE.value
                             )
    object_name = f"{object_name}.{extention}"
    s3_client.upload_file(f"{file_location}/{file_obj_name}", bucket, object_name,
                          ExtraArgs={'ACL': 'public-read'})
    public_url = f'https://{bucket}.s3-us-west-1.amazonaws.com/{object_name}'
    return public_url