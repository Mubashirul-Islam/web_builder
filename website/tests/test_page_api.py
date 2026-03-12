import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from website.models import Website, Page
from website.utils.upload_file import upload_file
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


class PageGETTests(TempMediaRootMixin, APITestCase):
    """Tests for GET requests to the Page API endpoints."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username="page-tester",
            email="pages@example.com",
            password="test-password",
        )

        cls.website = Website.objects.create(
            user=cls.user,
            name="Docs Site",
            description="Website for docs",
            url="https://docs.example.com",
            **website_files("docs-site-get"),
        )

        cls.page_1 = Page.objects.create(
            website=cls.website,
            title="Getting Started",
            slug="getting-started",
            meta_description="Getting Started page",
            meta_og_type="article",
            meta_og_image="https://docs.example.com/assets/getting-started-og.png",
            content=upload_file(
                "getting-started.txt", "<main>Start here</main>", "text/plain"
            ),
        )
        cls.page_2 = Page.objects.create(
            website=cls.website,
            title="API Reference",
            slug="api-reference",
            meta_description="API Reference page",
            meta_og_type="website",
            meta_og_image="https://docs.example.com/assets/api-reference-og.png",
            content=upload_file(
                "api-reference.txt", "<main>Endpoints</main>", "text/plain"
            ),
        )

    def test_page_list_returns_all_results(self):
        """Test that the page list endpoint returns all items."""
        response = self.client.get(reverse("page-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_page_list_supports_search_by_title(self):
        """Test that the page list endpoint supports searching by title."""
        response = self.client.get(reverse("page-list"), {"search": "Getting"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Getting Started")

    def test_page_list_honors_ordering_query_param(self):
        """Test that the page list endpoint honors the ordering query parameter."""
        response = self.client.get(reverse("page-list"), {"ordering": "created_at"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ordered_titles = [item["title"] for item in response.data]
        self.assertEqual(ordered_titles, ["Getting Started", "API Reference"])

    def test_page_list_supports_limit_offset_pagination(self):
        """Test that the page list endpoint supports limit and offset pagination."""
        first_page = self.client.get(
            reverse("page-list"),
            {"limit": 1, "offset": 0},
        )

        self.assertEqual(first_page.status_code, status.HTTP_200_OK)
        self.assertEqual(first_page.data["count"], 2)
        self.assertIsNone(first_page.data["previous"])
        self.assertIn("limit=1", first_page.data["next"])
        self.assertIn("offset=1", first_page.data["next"])
        self.assertEqual(len(first_page.data["results"]), 1)
        self.assertEqual(first_page.data["results"][0]["title"], "API Reference")

    def test_page_detail_returns_single_item(self):
        """Test that the page detail endpoint returns a single item."""
        response = self.client.get(reverse("page-detail", args=[self.page_1.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.page_1.pk)
        self.assertEqual(response.data["title"], "Getting Started")

    def test_page_detail_returns_404_for_missing_item(self):
        """Test that the page detail endpoint returns 404 for a missing item."""
        response = self.client.get(reverse("page-detail", args=[99999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PagePOSTTests(TempMediaRootMixin, APITestCase):
    """Tests for POST requests to the Page API endpoints."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username="page-tester",
            email="pages@example.com",
            password="test-password",
        )

        cls.website = Website.objects.create(
            user=cls.user,
            name="Docs Site",
            description="Website for docs",
            url="https://docs.example.com",
            **website_files("docs-site-post"),
        )

    def test_create_page_with_valid_data(self):
        """Test creating a page with valid data."""
        data = {
            "website": self.website.id,
            "title": "New Page",
            "slug": "new-page",
            "meta_description": "New Page meta description",
            "meta_og_type": "website",
            "meta_og_image": "https://docs.example.com/assets/new-page-og.png",
            "content": upload_file(
                "new-page.txt", "<main>This is new content</main>", "text/plain"
            ),
        }
        response = self.client.post(reverse("page-list"), data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Page.objects.count(), 1)
        self.assertEqual(response.data["title"], "New Page")
        self.assertEqual(response.data["slug"], "new-page")

    def test_create_page_with_missing_required_fields(self):
        """Test creating a page without required fields fails."""
        data = {
            "content": "Missing required fields",
        }
        response = self.client.post(reverse("page-list"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Page.objects.count(), 0)


class PagePUTTests(TempMediaRootMixin, APITestCase):
    """Tests for PUT requests to the Page API endpoints."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username="page-tester",
            email="pages@example.com",
            password="test-password",
        )

        cls.website = Website.objects.create(
            user=cls.user,
            name="Docs Site",
            description="Website for docs",
            url="https://docs.example.com",
            **website_files("docs-site-put"),
        )

        cls.page = Page.objects.create(
            website=cls.website,
            title="Original Page",
            slug="original-page",
            meta_description="Original Page meta description",
            meta_og_type="website",
            meta_og_image="https://docs.example.com/assets/original-page-og.png",
            content=upload_file(
                "original-page.txt", "<main>Original content</main>", "text/plain"
            ),
        )

    def test_update_page_with_valid_data(self):
        """Test updating a page with valid data using PUT."""
        data = {
            "website": self.website.id,
            "title": "Updated Page",
            "slug": "updated-page",
            "meta_description": "Updated Page meta description",
            "meta_og_type": "article",
            "meta_og_image": "https://docs.example.com/assets/updated-page-og.png",
            "content": upload_file(
                "updated-page.txt", "<main>Updated content</main>", "text/plain"
            ),
        }
        response = self.client.put(
            reverse("page-detail", args=[self.page.pk]),
            data,
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, "Updated Page")
        self.assertEqual(self.page.slug, "updated-page")
        self.assertEqual(self.page.meta_description, "Updated Page meta description")
        self.assertEqual(self.page.meta_og_type, "article")
        self.assertEqual(
            self.page.meta_og_image,
            "https://docs.example.com/assets/updated-page-og.png",
        )
        self.assertIn("updated-page", self.page.content.name)
        self.assertTrue(self.page.content.name.endswith(".txt"))

    def test_update_page_with_missing_required_fields(self):
        """Test updating a page with missing required fields fails."""
        data = {
            "content": "Only content",
        }
        response = self.client.put(
            reverse("page-detail", args=[self.page.pk]),
            data,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_nonexistent_page(self):
        """Test updating a nonexistent page returns 404."""
        data = {
            "website": self.website.id,
            "title": "Updated Page",
            "slug": "updated-page",
        }
        response = self.client.put(
            reverse("page-detail", args=[99999]),
            data,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PagePATCHTests(TempMediaRootMixin, APITestCase):
    """Tests for PATCH requests to the Page API endpoints."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username="page-tester",
            email="pages@example.com",
            password="test-password",
        )

        cls.website = Website.objects.create(
            user=cls.user,
            name="Docs Site",
            description="Website for docs",
            url="https://docs.example.com",
            **website_files("docs-site-patch"),
        )

        cls.page = Page.objects.create(
            website=cls.website,
            title="Original Page",
            slug="original-page",
            meta_description="Original Page meta description",
            meta_og_type="website",
            meta_og_image="https://docs.example.com/assets/original-page-og.png",
            content=upload_file(
                "original-page-patch.txt", "<main>Original content</main>", "text/plain"
            ),
        )

    def test_partial_update_page_title(self):
        """Test partially updating a page's title using PATCH."""
        data = {
            "title": "Partially Updated Page",
        }
        response = self.client.patch(
            reverse("page-detail", args=[self.page.pk]),
            data,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, "Partially Updated Page")
        self.assertEqual(self.page.slug, "original-page")
        self.assertEqual(self.page.meta_description, "Original Page meta description")
        self.assertEqual(self.page.meta_og_type, "website")
        self.assertEqual(
            self.page.meta_og_image,
            "https://docs.example.com/assets/original-page-og.png",
        )
        self.assertIn("original-page-patch", self.page.content.name)
        self.assertTrue(self.page.content.name.endswith(".txt"))

    def test_partial_update_nonexistent_page(self):
        """Test partially updating a nonexistent page returns 404."""
        data = {
            "title": "Updated Page",
        }
        response = self.client.patch(
            reverse("page-detail", args=[99999]),
            data,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PageDELETETests(TempMediaRootMixin, APITestCase):
    """Tests for DELETE requests to the Page API endpoints."""

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username="page-tester",
            email="pages@example.com",
            password="test-password",
        )

        cls.website = Website.objects.create(
            user=cls.user,
            name="Docs Site",
            description="Website for docs",
            url="https://docs.example.com",
            **website_files("docs-site-delete"),
        )

    def test_delete_page(self):
        """Test deleting a page."""
        page = Page.objects.create(
            website=self.website,
            title="Page to Delete",
            slug="delete-page",
            meta_description="Delete Page meta description",
            meta_og_type="website",
            meta_og_image="https://docs.example.com/assets/delete-page-og.png",
            content=upload_file(
                "delete-page.txt", "<main>Content to delete</main>", "text/plain"
            ),
        )
        response = self.client.delete(reverse("page-detail", args=[page.pk]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Page.objects.count(), 0)

    def test_delete_nonexistent_page(self):
        """Test deleting a nonexistent page returns 404."""
        response = self.client.delete(reverse("page-detail", args=[99999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
