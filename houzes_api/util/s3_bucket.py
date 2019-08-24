import boto3
from houzes_api import settings


def get_s3_bucket():
    s3_connection = boto3.resource('s3',
                                   region_name=settings.AWS_REGION,
                                   aws_access_key_id=settings.AWS_ACCESS_KEY,
                                   aws_secret_access_key=settings.AWS_SECRET_KEY)
    return s3_connection
