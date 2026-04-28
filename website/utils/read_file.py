from django.core.files.storage import default_storage


def read_file(path: str) -> str:
    try:
        with default_storage.open(path, "r") as f:
            return f.read()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"File '{path}' not found.") from exc
    except Exception as exc:
        raise OSError(f"Could not read file '{path}'.") from exc
