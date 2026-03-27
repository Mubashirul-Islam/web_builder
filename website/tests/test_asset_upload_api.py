import shutil
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from website.models import Asset, Website
from website.utils.website_files import website_files


class TempMediaRootMixin:
    """Use a temporary MEDIA_ROOT for tests that upload files."""

    @classmethod
    def setUpClass(cls):
        cls._temp_media_root = tempfile.mkdtemp(prefix="test-media-")
        cls._media_override = override_settings(MEDIA_ROOT=cls._temp_media_root)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls._media_override.disable()
        shutil.rmtree(cls._temp_media_root, ignore_errors=True)
        super().tearDownClass()


class AssetUploadTests(TempMediaRootMixin, APITestCase):
    """Tests for the website asset upload endpoint."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username="asset-tester",
            email="asset@example.com",
            password="test-password",
        )
        cls.website = Website.objects.create(
            user=cls.user,
            name="Asset Site",
            description="Site for asset upload tests",
            url="https://assets.example.com",
            **website_files("asset-site"),
        )

    def _upload_url(self, pk=None):
        return reverse("website-asset-upload", args=[pk or self.website.pk])

    @patch("website.views.AssetDimensions.get_dimensions", return_value=(800, 600))
    def test_asset_upload_creates_assets_and_returns_counts(self, _mock_dims):
        image = SimpleUploadedFile(
            "hero.png", b"fake-image-bytes", content_type="image/png"
        )
        video = SimpleUploadedFile(
            "intro.mp4", b"fake-video-bytes", content_type="video/mp4"
        )
        data = {
            "files": [image, video],
            "alt_texts": ["Homepage hero", "Intro animation"],
        }

        response = self.client.post(self._upload_url(), data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Assets uploaded successfully.")
        self.assertEqual(response.data["images"], 1)
        self.assertEqual(response.data["videos"], 1)
        self.assertEqual(Asset.objects.count(), 2)

    def test_asset_upload_returns_400_when_files_and_alt_texts_mismatch(self):
        image = SimpleUploadedFile(
            "hero.png", b"fake-image-bytes", content_type="image/png"
        )
        data = {
            "files": [image],
            "alt_texts": ["Hero", "Unexpected extra alt text"],
        }

        response = self.client.post(self._upload_url(), data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Asset.objects.count(), 0)

    def test_asset_upload_returns_400_for_unsupported_file_type(self):
        doc = SimpleUploadedFile(
            "notes.pdf", b"fake-pdf-bytes", content_type="application/pdf"
        )
        data = {
            "files": [doc],
            "alt_texts": ["PDF should be rejected"],
        }

        response = self.client.post(self._upload_url(), data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Asset.objects.count(), 0)

    def test_asset_upload_returns_404_for_nonexistent_website(self):
        image = SimpleUploadedFile(
            "hero.png", b"fake-image-bytes", content_type="image/png"
        )
        data = {
            "files": [image],
            "alt_texts": ["Hero image"],
        }

        response = self.client.post(
            self._upload_url(pk=99999), data, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Asset.objects.count(), 0)
