from enum import StrEnum


class ModelNames(StrEnum):
    """Supported model names used by upload path routing."""

    PAGE = "Page"
    WEBSITE = "Website"
    ASSET = "Asset"


class AssetTypes(StrEnum):
    """Supported asset media types."""

    IMAGE = "image"
    VIDEO = "video"
