from pathlib import Path

from django.conf import settings

from website.utils.read_file import read_file
from website.models import Website, Page


class WebsiteBuilder:
    """Build static website files for a Website instance in a target mode."""

    @classmethod
    def build_website(cls, website: Website, mode: str) -> None:
        """Generate HTML pages, static files, and copied assets."""
        output_dir = Path(settings.MEDIA_ROOT) / website.name / mode
        pages_dir = output_dir / "pages"
        static_dir = output_dir / "static"
        asset_dir = output_dir / "asset"

        header_content, footer_content, js_content, css_content = cls._read_contents(
            website
        )

        cls._prepare_output_dirs(output_dir, pages_dir, static_dir, asset_dir)

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
    def _prepare_output_dirs(
        output_dir: Path,
        pages_dir: Path,
        static_dir: Path,
        asset_dir: Path,
    ) -> None:
        """Create the target directories used by the build output."""
        output_dir.mkdir(parents=True, exist_ok=True)
        pages_dir.mkdir(parents=True, exist_ok=True)
        static_dir.mkdir(parents=True, exist_ok=True)
        asset_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _read_contents(website: Website) -> tuple[str, str, str, str]:
        '''Read the content of the website's header, footer, JavaScript, and CSS files.'''
        return (
            read_file(website.header),
            read_file(website.footer),
            read_file(website.js),
            read_file(website.css),
        )

    @staticmethod
    def _render_page_html(page: Page, header_content: str, page_content: str, footer_content: str) -> str:
        '''Render the full HTML for a page by combining its content with the website header and footer.'''

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
    def _write_page(pages_dir: Path, slug: str, html: str) -> None:
        """Write a single rendered page into the pages directory."""
        page_path = pages_dir / f"{slug}.html"
        page_path.write_text(html, encoding="utf-8")

    @staticmethod
    def _write_static_files(static_dir: Path, css_content: str, js_content: str) -> None:
        """Write website-level CSS and JavaScript assets."""
        css_path = static_dir / "style.css"
        js_path = static_dir / "script.js"

        css_path.write_text(css_content, encoding="utf-8")
        js_path.write_text(js_content, encoding="utf-8")

    @staticmethod
    def _write_asset_files(asset_dir: Path, website: Website) -> None:
        for asset in website.assets.all():
            target_dir = asset_dir / asset.type
            target_dir.mkdir(exist_ok=True)

            filename = Path(asset.file.name).name
            target_path = target_dir / filename

            with asset.file.open("rb") as src, target_path.open("wb") as dst:
                dst.write(src.read())
