from django.core.files.uploadedfile import SimpleUploadedFile

def upload_file(filename, content, content_type):
    return SimpleUploadedFile(
        filename, content.encode("utf-8"), content_type=content_type
    )