def read_file(field):
    """Read text content from a model FileField."""
    with field.open("r") as f:
        content = f.read()
    return content if isinstance(content, str) else content.decode("utf-8")
