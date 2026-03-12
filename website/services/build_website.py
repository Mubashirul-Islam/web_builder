from pathlib import Path
from django.conf import settings

from website.utils.read_file import read_file


def build_website(website, mode):
    """
    Build HTML files for all pages of a website.

    mode: "preview" or "live"
    Returns a list of output file paths written.
    """

    header_content = read_file(website.header)
    footer_content = read_file(website.footer)

    js_content = read_file(website.js)
    css_content = read_file(website.css)

    output_dir = Path(settings.BASE_DIR) / "storage" / mode / website.name
    output_dir.mkdir(parents=True, exist_ok=True)

    for page in website.pages.all():
        page_content = read_file(page.content)

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
        out_path.write_text(html, encoding="utf-8")

    output_static_dir = output_dir / "static"
    output_static_dir.mkdir(exist_ok=True)

    out_path_css = output_static_dir / "style.css"
    out_path_css.write_text(css_content, encoding="utf-8")

    out_path_js = output_static_dir / "script.js"
    out_path_js.write_text(js_content, encoding="utf-8")
