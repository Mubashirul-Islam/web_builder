from rest_framework import serializers
from website.models import Page, Website

class WebsiteSerializer(serializers.ModelSerializer):
    """Serializer for the Website model."""

    class Meta:
        model = Website
        fields = "__all__"


class PageSerializer(serializers.ModelSerializer):
    """Serializer for the Page model."""

    class Meta:
        model = Page
        fields = "__all__"
