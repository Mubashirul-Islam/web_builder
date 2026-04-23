import json
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from website.utils.read_file import read_file
from website.models import Website, Page


class WebsiteBuilder:
    """Build static website files for a Website instance in a target mode."""

    @classmethod
    def build_website(cls, website: Website, mode: str) -> None:
        """Generate JSON page payloads, static files, and copied assets."""
        output_dir = f"{website.name}/{mode}"
        pages_dir = f"{output_dir}/pages"
        static_dir = f"{output_dir}/static"
        asset_dir = f"{output_dir}/asset"
        css_url = default_storage.url(f"{static_dir}/style.css")
        js_url = default_storage.url(f"{static_dir}/script.js")

        header_content, footer_content, js_content, css_content = cls._read_contents(
            website
        )
        cls._write_shared_layout_files(output_dir, header_content, footer_content)

        for page in website.pages.all():
            try:
                page_content = read_file(page.content)
            except FileNotFoundError as exc:
                raise RuntimeError(
                    f"Failed to read content for page '{page.slug}'."
                ) from exc

            payload_json = cls._render_page_json(
                page,
                page_content,
                css_url,
                js_url,
            )
            cls._write_page(pages_dir, page.slug, payload_json)

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
    def _render_page_json(
        page: Page,
        page_content: str,
        css_url: str,
        js_url: str,
    ) -> str:
        """Serialize page metadata and content into the expected JSON payload."""

        payload = {
            "meta_description": page.meta_description,
            "title": page.title,
            "meta_og_type": page.meta_og_type,
            "meta_og_image": page.meta_og_image,
            "css_url": css_url,
            "js_url": js_url,
            "content": page_content,
            "dynamic_endpoint": page.dynamic_endpoint or "",
        }
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def _write_shared_layout_files(
        output_dir: str, header_content: str, footer_content: str
    ) -> None:
        """Write shared header and footer JSON files once per website build."""
        header_path = f"{output_dir}/header.json"
        footer_path = f"{output_dir}/footer.json"

        header_payload = json.dumps({"header": header_content}, ensure_ascii=False)
        footer_payload = json.dumps({"footer": footer_content}, ensure_ascii=False)

        WebsiteBuilder._write_bytes(header_path, header_payload.encode("utf-8"))
        WebsiteBuilder._write_bytes(footer_path, footer_payload.encode("utf-8"))

    @staticmethod
    def _write_page(pages_dir: str, slug: str, payload_json: str) -> None:
        """Write a single page JSON payload into the pages directory."""
        page_path = f"{pages_dir}/{slug}.json"
        WebsiteBuilder._write_bytes(page_path, payload_json.encode("utf-8"))

    @staticmethod
    def _write_static_files(static_dir: str, css_content: str, js_content: str) -> None:
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

            try:
                if default_storage.exists(target_path):
                    default_storage.delete(target_path)

                default_storage.save(target_path, asset.file)
            except Exception as exc:
                raise OSError(
                    f"Could not write asset '{filename}' to '{target_path}'."
                ) from exc

    @staticmethod
    def _write_bytes(path: str, content: bytes) -> None:
        """Write bytes to storage, replacing any existing file at the same path."""
        try:
            if default_storage.exists(path):
                default_storage.delete(path)
            default_storage.save(path, ContentFile(content))
        except Exception as exc:
            raise OSError(f"Could not write file '{path}'.") from exc
