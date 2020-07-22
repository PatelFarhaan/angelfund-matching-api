import magic
import shutil
from flask import jsonify
from common_utilities.mime_files_upload import profile_pic_upload_to_s3, pdf_upload_to_s3


def str_file_upload(file_location, file_name, file_type, user_obj):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(f"{file_location}/{file_name}")
    mime_base = mime_type.split('/', 1)[0]  # base mime type :=> application (for pdf) or image (for image)
    mime_extention = mime_type.split('/', 1)[1]  # pdf or jpeg

    if file_type == "application":
        if mime_extention == "pdf":
            pdf_url = pdf_upload_to_s3(file_name, mime_extention, file_location, file_name)
            user_obj.slide_deck = pdf_url
            user_obj.save()
            shutil.rmtree(file_location)
            return jsonify({"result": True, "url": pdf_url})
        else:
            shutil.rmtree(file_location)
            return jsonify({"result": False, "error": "pdf file required"})

    elif file_type == "image":
        if mime_base == "image":
            image_url = profile_pic_upload_to_s3(file_name, mime_extention, file_location, file_name)
            user_obj.profile_pic_link = image_url
            user_obj.save()
            shutil.rmtree(file_location)
            return jsonify({"result": True, "url": image_url})
        else:
            shutil.rmtree(file_location)
            return jsonify({"result": False, "error": "image file required"})

    else:
        shutil.rmtree(file_location)
        return jsonify({"result": False, "error": "invalid file type"})