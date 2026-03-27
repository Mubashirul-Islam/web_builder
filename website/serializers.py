from rest_framework import serializers
from website.models import Asset, Page, Website


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


class AssetSerializer(serializers.Serializer):
    """Serializer for the Asset model."""

    files = serializers.ListField(
        child=serializers.FileField(),
    )

    alt_texts = serializers.ListField(
        child=serializers.CharField(),
    )

    def validate(self, data):

        if len(data["files"]) != len(data["alt_texts"]):
            raise serializers.ValidationError(
                "The number of files must match the number of alt_texts."
            )

        validated = []
        for f, alt_text in zip(data["files"], data["alt_texts"]):
            if f.content_type.startswith("image/"):
                file_type = Asset.AssetType.IMAGE
            elif f.content_type.startswith("video/"):
                file_type = Asset.AssetType.VIDEO
            else:
                raise serializers.ValidationError(
                    f"Unsupported file type: {f.name}. Allowed: images/videos only."
                )
            validated.append((f, file_type, alt_text))

        return validated
