from pathlib import Path

from django.conf import settings

from website.utils.read_file import read_file


def build_website(website, mode):
    """Build the static website files for the given Website instance and mode.

    Args:
        website: The Website instance to build.
        mode: The build mode, either 'preview' or 'live'."""

    header_content, footer_content, js_content, css_content = _read_assets(website)

    output_dir = Path(settings.MEDIA_ROOT) / website.name / mode
    pages_dir = output_dir / "pages"
    static_dir = output_dir / "static"
    asset_dir = output_dir / "asset"

    output_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)

    pages = website.pages.all()

    for page in pages:
        page_content = read_file(page.content)
        html = _render_page_html(page, header_content, page_content, footer_content)
        _write_page(pages_dir, page.slug, html)

    _write_static_files(static_dir, css_content, js_content)

    _write_asset_files(asset_dir, website)


def _read_assets(website):
    return (
        read_file(website.header),
        read_file(website.footer),
        read_file(website.js),
        read_file(website.css),
    )


def _render_page_html(page, header_content, page_content, footer_content):
    return f"""<!DOCTYPE html>
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


def _write_page(pages_dir, slug, html):
    page_path = pages_dir / f"{slug}.html"
    page_path.write_text(html, encoding="utf-8")


def _write_static_files(static_dir, css_content, js_content):
    css_path = static_dir / "style.css"
    js_path = static_dir / "script.js"

    css_path.write_text(css_content, encoding="utf-8")
    js_path.write_text(js_content, encoding="utf-8")


def _write_asset_files(asset_dir, website):
    for asset in website.assets.all():
        target_dir = asset_dir / ("images" if asset.type == "image" else "videos")
        target_dir.mkdir(exist_ok=True)

        filename = Path(asset.file.name).name
        target_path = target_dir / filename

        with asset.file.open("rb") as src, target_path.open("wb") as dst:
            dst.write(src.read())
