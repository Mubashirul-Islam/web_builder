from django.core.files.storage import default_storage
from django.core.files import File

def write_file(path: str, file: File) -> None:
    try:
        if default_storage.exists(path):
            default_storage.delete(path)
        default_storage.save(path, file)
    except Exception as exc:
        raise OSError(f"Could not write file '{path}'.") from exc