from django.core.files.uploadedfile import SimpleUploadedFile

from website.utils.upload_file import upload_file


def website_files(prefix: str) -> dict[str, SimpleUploadedFile]:
    """Build the standard uploaded files bundle used to create a website."""
    return {
        "css": upload_file(f"{prefix}.css", "body{margin:0;}", "text/css"),
        "js": upload_file(
            f"{prefix}.js", "console.log('ok');", "application/javascript"
        ),
        "header": upload_file(
            f"{prefix}-header.txt", "<header>Header</header>", "text/plain"
        ),
        "footer": upload_file(
            f"{prefix}-footer.txt", "<footer>Footer</footer>", "text/plain"
        ),
    }
