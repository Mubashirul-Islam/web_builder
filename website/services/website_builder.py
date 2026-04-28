import json
from pathlib import Path

from django.db.models.fields.files import FieldFile
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from render.services.dynamic_data import DynamicDataService
from website.models import Website, Page
from website.utils.js_snippet import js_snippet
from website.utils.write_file import write_file


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
                page_content = cls._read_file_field(page.content)
            except FileNotFoundError as exc:
                raise RuntimeError(
                    f"Failed to read content for page '{page.slug}'."
                ) from exc
            property_list = DynamicDataService.fetch_property_list(website)

            payload_json = cls._render_page_json(
                page,
                page_content,
                css_url,
                js_url,
                property_list,
            )
            cls._write_page(pages_dir, page.slug, payload_json)

        js_content = cls._append_js_snippet(js_content, js_snippet(website, page))
        cls._write_static_files(static_dir, css_content, js_content)
        cls._write_asset_files(asset_dir, website)

    @classmethod
    def _read_contents(cls, website: Website) -> tuple[str, str, str, str]:
        """Read the content of the website's header, footer, JavaScript, and CSS files."""
        return (
            cls._read_file_field(website.header),
            cls._read_file_field(website.footer),
            cls._read_file_field(website.js),
            cls._read_file_field(website.css),
        )

    @staticmethod
    def _render_page_json(
        page: Page,
        page_content: str,
        css_url: str,
        js_url: str,
        property_list: dict,
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
            "property_list": property_list,
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

        write_file(header_path, ContentFile(header_payload.encode("utf-8")))
        write_file(footer_path, ContentFile(footer_payload.encode("utf-8")))

    @staticmethod
    def _write_page(pages_dir: str, slug: str, payload_json: str) -> None:
        """Write a single page JSON payload into the pages directory."""
        page_path = f"{pages_dir}/{slug}.json"
        write_file(page_path, ContentFile(payload_json.encode("utf-8")))

    @staticmethod
    def _write_static_files(static_dir: str, css_content: str, js_content: str) -> None:
        """Write website-level CSS and JavaScript assets."""
        css_path = f"{static_dir}/style.css"
        js_path = f"{static_dir}/script.js"

        write_file(css_path, ContentFile(css_content.encode("utf-8")))
        write_file(js_path, ContentFile(js_content.encode("utf-8")))

    @staticmethod
    def _append_js_snippet(js_content: str, snippet: str) -> str:
        """Append a JavaScript snippet to the end of JS content."""
        if not snippet:
            return js_content
        separator = "\n" if js_content and not js_content.endswith("\n") else ""
        return f"{js_content}{separator}{snippet}"

    @staticmethod
    def _write_asset_files(asset_dir: str, website: Website) -> None:
        for asset in website.assets.all():
            filename = Path(asset.file.name).name
            target_path = f"{asset_dir}/{asset.type}/{filename}"
            write_file(target_path, asset.file)

    @staticmethod
    def _read_file_field(field: FieldFile) -> str:
        """Read text content from a model FileField."""
        try:
            with field.open("r") as f:
                content = f.read()
            return content if isinstance(content, str) else content.decode("utf-8")
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"File '{field.name}' was not found.") from exc
