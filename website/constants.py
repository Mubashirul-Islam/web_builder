from enum import StrEnum


class ModelNames(StrEnum):
    PAGE = "Page"
    WEBSITE = "Website"
    ASSET = "Asset"


class AssetTypes(StrEnum):
    IMAGE = "image"
    VIDEO = "video"
