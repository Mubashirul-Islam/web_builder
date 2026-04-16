from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from website.utils.read_file import read_file
from website.models import Website, Page


class WebsiteBuilder:
    """Build static website files for a Website instance in a target mode."""

    @classmethod
    def build_website(cls, website: Website, mode: str) -> None:
        """Generate HTML pages, static files, and copied assets."""
        output_dir = f"{website.name}/{mode}"
        pages_dir = f"{output_dir}/pages"
        static_dir = f"{output_dir}/static"
        asset_dir = f"{output_dir}/asset"

        header_content, footer_content, js_content, css_content = cls._read_contents(
            website
        )

        for page in website.pages.all():
            page_content = read_file(page.content)
            html = cls._render_page_html(
                page,
                header_content,
                page_content,
                footer_content,
            )
            cls._write_page(pages_dir, page.slug, html)

        cls._write_static_files(static_dir, css_content, js_content)
        cls._write_asset_files(asset_dir, website)

    @staticmethod
    def _read_contents(website: Website) -> tuple[str, str, str, str]:
        """Read the content of the website's header, footer, JavaScript, and CSS files."""
        return (
            read_file(website.header),
            read_file(website.footer),
            read_file(website.js),
            read_file(website.css),
        )

    @staticmethod
    def _render_page_html(
        page: Page, header_content: str, page_content: str, footer_content: str
    ) -> str:
        """Render the full HTML for a page by combining its content with the website header and footer."""

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

    @staticmethod
    def _write_page(pages_dir: str, slug: str, html: str) -> None:
        """Write a single rendered page into the pages directory."""
        page_path = f"{pages_dir}/{slug}.html"
        WebsiteBuilder._write_bytes(page_path, html.encode("utf-8"))

    @staticmethod
    def _write_static_files(
        static_dir: str, css_content: str, js_content: str
    ) -> None:
        """Write website-level CSS and JavaScript assets."""
        css_path = f"{static_dir}/style.css"
        js_path = f"{static_dir}/script.js"

        WebsiteBuilder._write_bytes(css_path, css_content.encode("utf-8"))
        WebsiteBuilder._write_bytes(js_path, js_content.encode("utf-8"))

    @staticmethod
    def _write_asset_files(asset_dir: str, website: Website) -> None:
        for asset in website.assets.all():
            filename = Path(asset.file.name).name
            target_path = f"{asset_dir}/{asset.type}/{filename}"

            if default_storage.exists(target_path):
                default_storage.delete(target_path)

            default_storage.save(target_path, asset.file)

    @staticmethod
    def _write_bytes(path: str, content: bytes) -> None:
        """Write bytes to storage, replacing any existing file at the same path."""
        if default_storage.exists(path):
            default_storage.delete(path)
        default_storage.save(path, ContentFile(content))
