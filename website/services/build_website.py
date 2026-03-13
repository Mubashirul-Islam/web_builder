from pathlib import Path
from django.conf import settings

from website.utils.read_file import read_file


def build_website(website, mode):
    """Build the static website files for the given Website instance and mode.

    Args:
        website: The Website instance to build.
        mode: The build mode, either 'preview' or 'live'."""

    header_content = read_or_fail(website.header, "Failed to read website header file.")
    footer_content = read_or_fail(website.footer, "Failed to read website footer file.")
    js_content = read_or_fail(website.js, "Failed to read website JavaScript file.")
    css_content = read_or_fail(website.css, "Failed to read website CSS file.")

    output_dir = Path(settings.BASE_DIR) / "storage" / mode / website.name
    mkdir_or_fail(
        output_dir,
        "Failed to create website output directory.",
        parents=True,
        exist_ok=True,
    )

    try:
        pages = website.pages.all()
    except Exception as exc:
        raise RuntimeError("Failed to load website pages.") from exc

    for page in pages:
        page_content = read_or_fail(
            page.content,
            f"Failed to read content for page '{page.slug}'.",
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{page.meta_description}">
<meta property="og:title" content="{page.title}">
<meta property="og:description" content="{page.meta_description}">
<meta property="og:type" content="{page.meta_og_type}">
<meta property="og:image" content="{page.meta_og_image}">
<title>{page.title}</title>
<link rel="stylesheet" href="static/style.css">
<script src="static/script.js" defer></script>
</head>
<body>
{header_content}
{page_content}
{footer_content}
</body>
</html>"""

        out_path = output_dir / f"{page.slug}.html"
        write_or_fail(
            out_path,
            html,
            f"Failed to write HTML output for page '{page.slug}'.",
        )

    output_static_dir = output_dir / "static"
    mkdir_or_fail(output_static_dir, "Failed to create static output directory.")

    out_path_css = output_static_dir / "style.css"
    write_or_fail(out_path_css, css_content, "Failed to write CSS output file.")

    out_path_js = output_static_dir / "script.js"
    write_or_fail(out_path_js, js_content, "Failed to write JavaScript output file.")


def read_or_fail(file_field, error_message):
    try:
        return read_file(file_field)
    except Exception as exc:
        raise RuntimeError(error_message) from exc


def write_or_fail(path, content, error_message):
    try:
        path.write_text(content, encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(error_message) from exc


def mkdir_or_fail(path, error_message, parents=False, exist_ok=True):
    try:
        path.mkdir(parents=parents, exist_ok=exist_ok)
    except Exception as exc:
        raise RuntimeError(error_message) from exc
