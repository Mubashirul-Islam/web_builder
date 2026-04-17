from django.db.models.fields.files import FieldFile


def read_file(field: FieldFile) -> str:
    """Read text content from a model FileField."""
    try:
        with field.open("r") as f:
            content = f.read()

        return content if isinstance(content, str) else content.decode("utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"File '{field.name}' was not found.") from exc
