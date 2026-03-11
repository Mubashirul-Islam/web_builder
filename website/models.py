from django.db import models
from django.core.validators import FileExtensionValidator

from django.contrib.auth.models import User
from .utils.asset_upload_path import asset_upload_path


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
        upload_to=asset_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["css"])],
        help_text="The CSS file for the website.",
    )
    js = models.FileField(
        upload_to=asset_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["js"])],
        help_text="The JavaScript file for the website.",
    )
    header = models.FileField(
        upload_to=asset_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["txt"])],
        help_text="The header file for the website.",
    )
    footer = models.FileField(
        upload_to=asset_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["txt"])],
        help_text="The footer file for the website.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
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
        upload_to=asset_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["txt"])],
        help_text="The content file for the page.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return self.title
