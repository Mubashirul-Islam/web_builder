import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.core.files.storage import default_storage

from render.services.dynamic_data import DynamicDataService


def render_page(
    request: HttpRequest, website_name: str, page_slug: str
) -> HttpResponse:
    """Render an HTML page by combining JSON payloads stored in default storage."""

    output_dir = f"{website_name}/live"
    page_path = f"{output_dir}/pages/{page_slug}.json"
    header_path = f"{output_dir}/header.json"
    footer_path = f"{output_dir}/footer.json"

    try:
        with default_storage.open(page_path, "r") as f:
            page_payload = json.load(f)

        with default_storage.open(header_path, "r") as f:
            header_payload = json.load(f)

        with default_storage.open(footer_path, "r") as f:
            footer_payload = json.load(f)
    except FileNotFoundError:
        return HttpResponse("Page not found", status=404)
    except json.JSONDecodeError:
        return HttpResponse("Invalid page data", status=500)

    dynamic_data = DynamicDataService.fetch_dynamic_data(
        page_payload.get("dynamic_endpoint", "")
    )

    rendered_content = DynamicDataService.render_content_template(
        page_payload.get("content", ""), dynamic_data
    )

    context = {
        "meta_description": page_payload.get("meta_description", ""),
        "title": page_payload.get("title", ""),
        "meta_og_type": page_payload.get("meta_og_type", ""),
        "meta_og_image": page_payload.get("meta_og_image", ""),
        "css_url": page_payload.get("css_url", ""),
        "js_url": page_payload.get("js_url", ""),
        "header_content": header_payload.get("header", ""),
        "page_content": rendered_content,
        "footer_content": footer_payload.get("footer", ""),
    }

    return render(request, "index.html", context)
