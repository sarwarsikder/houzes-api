from houzes_api import settings
from houzes_api.util.s3_bucket import get_s3_bucket

def file_upload(file, file_path):
    s3_bucket = get_s3_bucket()

    response = s3_bucket.Object(settings.S3_BUCKET_NAME, file_path).put(Body=file, ACL='public-read')
    if 'ResponseMetadata' in response and 'HTTPStatusCode' in response['ResponseMetadata'] and \
            response['ResponseMetadata']['HTTPStatusCode'] == 200:

        return True

    return False
