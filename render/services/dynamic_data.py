from website.models import Website


class DynamicDataService:
    """Service to fetch dynamic data for a website and render it into templates."""

    @staticmethod
    def fetch_property_list(website: Website) -> dict:
        """Fetch the property list for the website and return it as a dict."""
        property_list = website.property_lists.first()
        if not property_list:
            return {}
        return {
            "section_id": property_list.section_id,
            "total_items": property_list.total_items,
            "orientation": property_list.orientation,
            "items_per_row": property_list.items_per_row,
            "item_list": property_list.item_list,
            "provider": property_list.provider,
            "type": property_list.type,
            "location": property_list.location,
            "source_url": property_list.source_url,
        }
