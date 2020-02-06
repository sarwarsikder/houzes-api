import io
import traceback
from PIL import Image
from django.core.files.storage import default_storage
from PIL import ImageOps


def image_upload(img_file, file_path, file_name, with_thumb):
    data = {}
    try:
        if file_path and file_name:
            img_file = ImageOps.exif_transpose(img_file)
            im = Image.open(img_file)
            buf = io.BytesIO()
            im.save(buf, format="png")
            byte_im = buf.getvalue()
            full_img_path = file_path + file_name
            s3_file_obj = default_storage.open(full_img_path, 'wb')
            s3_file_obj.write(byte_im)
            s3_file_obj.close()
            data['full_img_url'] = default_storage.url(full_img_path)

            if with_thumb:
                thumb_path = file_path+"thumb/"+file_name
                im = Image.open(img_file)

                with im as image:
                    width, height = image.size
                    if height <= 200 or width <= 200:
                        im_resize = image
                    else:
                        im_resize = im.resize((200, 200))
                # im_resize = im.resize((200, 200))
                buf = io.BytesIO()
                im_resize.save(buf, format="png")
                byte_im = buf.getvalue()
                s3_file_obj = default_storage.open(thumb_path, 'wb')
                s3_file_obj.write(byte_im)
                s3_file_obj.close()
                data['thumb_url'] = default_storage.url(thumb_path)
            data["status"] = True
            data["msg"] = "Successfully Image uploaded to s3."
        else:
            data["status"] = False
            data['msg'] = "File parameter missing error !!! Please check image name, path and file."
        return data
    except Exception as ex:
        traceback.print_exc()
        data["status"] = False
        data["msg"] = "Failed to upload. Reason = "+str(ex)
        return data
