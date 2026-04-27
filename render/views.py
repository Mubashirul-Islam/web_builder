import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from render.services.dynamic_data import DynamicDataService
from website.utils.read_file import read_file


def render_page(
    request: HttpRequest, website_name: str, page_slug: str
) -> HttpResponse:
    """Render an HTML page by combining JSON payloads stored in default storage."""

    output_dir = f"{website_name}/live"
    page_path = f"{output_dir}/pages/{page_slug}.json"
    header_path = f"{output_dir}/header.json"
    footer_path = f"{output_dir}/footer.json"

    try:
        page_payload = json.loads(read_file(page_path))
        header_payload = json.loads(read_file(header_path))
        footer_payload = json.loads(read_file(footer_path))
    except FileNotFoundError:
        return HttpResponse("Page not found", status=404)
    except json.JSONDecodeError:
        return HttpResponse("Invalid page data", status=500)

    dynamic_data = page_payload.get("dynamic_data", {})

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
