from django.core.files.uploadedfile import SimpleUploadedFile


def upload_file(filename: str, content: str, content_type: str) -> SimpleUploadedFile:
    """Create an in-memory uploaded file from UTF-8 text content."""
    return SimpleUploadedFile(
        filename, content.encode("utf-8"), content_type=content_type
    )
