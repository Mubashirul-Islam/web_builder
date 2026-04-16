from django.http import HttpRequest, HttpResponse
from django.core.files.storage import default_storage


def render_page(
    request: HttpRequest, website_name: str, page_slug: str
) -> HttpResponse:
    """Render a static HTML page for the given website and page slug."""

    path = f"{website_name}/live/pages/{page_slug}.html"

    try:
        with default_storage.open(path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return HttpResponse("Page not found", status=404)

    return HttpResponse(content, content_type="text/html")
