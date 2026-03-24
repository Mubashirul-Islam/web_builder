from django.contrib import admin

# Register your models here.
from .models import Asset, Website, Page


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    """Admin class for the Website model."""

    list_display = ("name", "url", "user", "modified_at")
    search_fields = ("name", "url")
    list_filter = ("created_at", "modified_at")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Admin class for the Page model."""

    list_display = ("title", "slug", "website", "modified_at")
    search_fields = ("title", "slug")
    list_filter = ("created_at", "modified_at")

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    """Admin class for the Asset model."""

    list_display = ("file", "type", "website", "size", "modified_at")
    search_fields = ("file",)
    list_filter = ("type", "modified_at")    
