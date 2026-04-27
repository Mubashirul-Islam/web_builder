import requests
from django.template import Context, Template


class DynamicDataService:
    """Service for fetching dynamic data and rendering content templates."""

    @staticmethod
    def fetch_dynamic_data(endpoint: str) -> dict:
        """Call the outside API and return parsed JSON, or empty dict on failure."""
        if not endpoint:
            return {}
        try:
            res = requests.get(endpoint, timeout=5)
            res.raise_for_status()
            return res.json()
        except Exception:
            return {}

    @staticmethod
    def render_content_template(page_content: str, dynamic_data: dict) -> str:
        """Render page content as a Django template so it can reference dynamic_data."""
        try:
            content_template = Template(page_content)
            return content_template.render(Context({"dynamic_data": dynamic_data}))
        except Exception:
            return page_content  # fall back to raw content if template is broken
