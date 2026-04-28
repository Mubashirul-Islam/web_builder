from django.db import models
from django.core.validators import FileExtensionValidator

from django.contrib.auth.models import User
from website.utils.upload_path import upload_path


class Website(models.Model):
    """Model representing a website."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="websites",
        help_text="The user who owns this website.",
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The name of the website. This will be used as the directory name for storing assets.",
    )
    description = models.TextField(
        blank=True, default="", help_text="A brief description of the website."
    )
    url = models.URLField(
        max_length=500,
        unique=True,
        help_text="The URL where the website will be hosted.",
    )
    css = models.FileField(
        upload_to=upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["css"])],
        help_text="The CSS file for the website.",
    )
    js = models.FileField(
        upload_to=upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["js"])],
        help_text="The JavaScript file for the website.",
    )
    header = models.FileField(
        upload_to=upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["txt"])],
        help_text="The header file for the website.",
    )
    footer = models.FileField(
        upload_to=upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["txt"])],
        help_text="The footer file for the website.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self) -> str:
        """Return the website name for admin and logs."""
        return self.name


class Page(models.Model):
    """Model representing a page within a website."""

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="pages",
        help_text="The website to which this page belongs.",
    )
    title = models.CharField(
        max_length=255, db_index=True, help_text="The title of the page."
    )
    slug = models.SlugField(max_length=255, help_text="The slug for the page.")
    meta_description = models.TextField(
        blank=True, default="", help_text="A brief description of the page."
    )
    meta_og_type = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="The Open Graph type for the page (e.g., 'website', 'article').",
    )
    meta_og_image = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text="The URL of the Open Graph image for the page.",
    )
    content = models.FileField(
        upload_to=upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["txt"])],
        help_text="The content file for the page.",
    )
    dynamic_endpoint = models.URLField(
        blank=True,
        null=True,
        help_text="Optional API endpoint to fetch dynamic data for the page.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self) -> str:
        """Return the page title for admin and logs."""
        return self.title


class Asset(models.Model):
    """Model representing an asset associated with a website."""

    class AssetType(models.TextChoices):
        """Allowed asset media categories."""

        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="assets",
        help_text="The website to which this asset belongs.",
    )
    file = models.FileField(
        upload_to=upload_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "jpg",
                    "jpeg",
                    "png",
                    "gif",
                    "webp",
                    "mp4",
                    "mov",
                    "avi",
                    "mkv",
                    "webm",
                ]
            )
        ],
        help_text="Uploaded asset file (image or video).",
    )
    type = models.CharField(
        max_length=10,
        choices=AssetType.choices,
        help_text="Detected asset type.",
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Alternative text for the asset.",
    )
    height = models.IntegerField(
        null=True,
        blank=True,
        help_text="Height of the image in pixels.",
    )
    width = models.IntegerField(
        null=True,
        blank=True,
        help_text="Width of the image in pixels.",
    )
    size = models.BigIntegerField(help_text="Size of the uploaded file in bytes.")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self) -> str:
        """Return a readable label with type and file name."""
        return f"{self.type} - {self.file.name}"


class PropertyList(models.Model):
    """Model representing a list of properties for a website."""

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="property_lists",
        help_text="The website to which this property list belongs.",
    )

    section_id = models.CharField(
        max_length=100,
        help_text="The section ID this property list is associated with.",
    )
    total_items = models.IntegerField(
        help_text="The total number of properties in this list."
    )
    orientation = models.CharField(
        max_length=10,
        choices=[("grid", "Grid"), ("list", "List")],
        help_text="The orientation of the property list.",
    )
    items_per_row = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of items per row (applicable if orientation is 'row').",
    )
    item_list = models.JSONField(
        help_text="A JSON array containing the list of properties. Each property should include details such as title, location, price, etc."
    )
    provider = models.CharField(
        max_length=50,
        help_text="The data provider for the property list (e.g., 'booking', 'airbnb').",
    )
    type = models.CharField(
        max_length=50,
        help_text="The type of properties in the list (e.g., 'hotel', 'apartment').",
    )
    location = models.CharField(
        max_length=255,
        help_text="The location associated with the property list (e.g., 'New York City').",
    )
    source_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text="Optional URL to the source of the property data.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self) -> str:
        """Return a label indicating the property list and associated website."""
        return f"Property List for {self.website.name}"
