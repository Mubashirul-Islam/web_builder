import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from website.models import Page, Website
from website.utils.upload_file import upload_file
from website.utils.website_files import website_files


class TempDirsMixin:
    """Use temporary directories for MEDIA_ROOT and BASE_DIR during tests."""

    @classmethod
    def setUpClass(cls):
        cls._temp_media_root = tempfile.mkdtemp(prefix="test-media-")
        cls._temp_base_dir = tempfile.mkdtemp(prefix="test-base-")
        cls._overrides = override_settings(
            MEDIA_ROOT=cls._temp_media_root,
            BASE_DIR=cls._temp_base_dir,
        )
        cls._overrides.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls._overrides.disable()
        shutil.rmtree(cls._temp_media_root, ignore_errors=True)
        shutil.rmtree(cls._temp_base_dir, ignore_errors=True)
        super().tearDownClass()


class WebsiteBuildTests(TempDirsMixin, APITestCase):
    """Tests for the website build endpoint."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username="build-tester",
            email="build@example.com",
            password="test-password",
        )

        cls.website = Website.objects.create(
            user=cls.user,
            name="Build Site",
            description="Site for build tests",
            url="https://build.example.com",
            **website_files("build-site"),
        )

        cls.page = Page.objects.create(
            website=cls.website,
            title="Home",
            slug="home",
            meta_description="Home page",
            meta_og_type="website",
            meta_og_image="https://build.example.com/assets/home-og.png",
            content=upload_file("home.txt", "<main>Welcome</main>", "text/plain"),
        )

    def _build_url(self, pk=None, mode=None):
        url = reverse("website-build", args=[pk or self.website.pk])
        if mode is not None:
            url += f"?mode={mode}"
        return url

    def test_build_preview_returns_200(self):
        response = self.client.post(self._build_url(mode="preview"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_build_live_returns_200(self):
        response = self.client.post(self._build_url(mode="live"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_build_returns_400_when_mode_missing(self):
        response = self.client.post(self._build_url(mode=None))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_build_returns_400_for_invalid_mode(self):
        response = self.client.post(self._build_url(mode="staging"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_build_returns_400_when_website_has_no_pages(self):
        empty_website = Website.objects.create(
            user=self.user,
            name="Empty Site",
            description="No pages",
            url="https://empty.example.com",
            **website_files("empty-site"),
        )
        response = self.client.post(
            reverse("website-build", args=[empty_website.pk]) + "?mode=preview"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_build_returns_404_for_nonexistent_website(self):
        response = self.client.post(self._build_url(pk=99999, mode="preview"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
