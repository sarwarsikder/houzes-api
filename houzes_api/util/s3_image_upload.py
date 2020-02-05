import io
import traceback
from PIL import Image
from django.core.files.storage import default_storage


def image_upload(img_file, file_path, file_name, with_thumb):
    data = {}
    try:
        if file_path and file_name:
            im = Image.open(img_file)
            buf = io.BytesIO()
            im.save(buf, format="png")
            byte_im = buf.getvalue()
            full_img_path = file_path +file_name
            s3_file_obj = default_storage.open(full_img_path, 'wb')
            s3_file_obj.write(byte_im)
            s3_file_obj.close()
            data['full_img_url'] = default_storage.url(full_img_path)

            if with_thumb:
                thumb_path = file_path+"thumb/"+file_name
                im = Image.open(img_file)
                im_resize = im.resize((100, 120))
                buf = io.BytesIO()
                im_resize.save(buf, format="png")
                byte_im = buf.getvalue()
                s3_file_obj = default_storage.open(thumb_path, 'wb')
                s3_file_obj.write(byte_im)
                s3_file_obj.close()
                data['thumb_url'] = default_storage.url(thumb_path)
            data["msg"] = "Successfully Image uploaded to s3."
        else:
            data['msg'] = "File parameter missing error !!! Please check image name, path and file."
        return data
    except Exception as ex:
        traceback.print_exc()
        data["msg"] = "Failed to upload. Reason = "+str(ex)
        return data
