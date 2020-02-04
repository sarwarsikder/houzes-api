import io
import traceback

from houzes_api import settings
from houzes_api.util.s3_bucket import get_s3_bucket
from PIL import Image
from django.core.files.storage import default_storage


def file_upload(file, file_path):

    try:

        im = Image.open(file)
        buf = io.BytesIO()
        im.save(buf, format='JPEG')
        byte_im = buf.getvalue()
        s3_file_obj = default_storage.open(file_path, 'wb')
        s3_file_obj.write(byte_im)
        s3_file_obj.close()

        #
        # screen_shot_path =   file_path
        # im = Image.open(file)
        # im_resize = im.resize((100, 120))
        # buf = io.BytesIO()
        # im_resize.save(buf, format='jpg')
        # byte_im = buf.getvalue()
        # s3_file_obj = default_storage.open(screen_shot_path, 'wb')
        # s3_file_obj.write(byte_im)
        # s3_file_obj.close()

    # response = s3_bucket.Object(settings.S3_BUCKET_NAME, file_path).put(Body=file, ACL='public-read')
    # if 'ResponseMetadata' in response and 'HTTPStatusCode' in response['ResponseMetadata'] and \
    #         response['ResponseMetadata']['HTTPStatusCode'] == 200:

        return True

    except Exception as ex:
        traceback.print_exc()
        return False
