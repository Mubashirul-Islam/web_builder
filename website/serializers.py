from rest_framework import serializers
from website.models import Page, Website


class PageSerializer(serializers.ModelSerializer):
    """Serializer for the Page model."""

    class Meta:
        model = Page
        fields = "__all__"


class WebsiteSerializer(serializers.ModelSerializer):
    """Serializer for the Website model."""
    pages = PageSerializer(many=True, read_only=True)

    class Meta:
        model = Website
        fields = "__all__"


class WebsiteBuildSerializer(serializers.Serializer):
    """Serializer for building a website."""

    mode = serializers.ChoiceField(choices=["preview", "live"])

    def validate(self, attrs):
        """Validate that the website has at least one page before building."""

        if not self.instance.pages.exists():
            raise serializers.ValidationError(  
                {"error": "Cannot build website with no pages."}
            )
        return attrs
