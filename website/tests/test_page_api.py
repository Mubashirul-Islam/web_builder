from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from website.models import Website, Page


class PageAPITests(APITestCase):
	'''Tests for the Page API endpoints.'''
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
		)

		cls.page_1 = Page.objects.create(
			website=cls.website,
			title="Getting Started",
			slug="getting-started",
			content="Start here",
		)
		cls.page_2 = Page.objects.create(
			website=cls.website,
			title="API Reference",
			slug="api-reference",
			content="Endpoints",
		)

	def test_page_list_returns_all_results(self):
		response = self.client.get(reverse("page-list"))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 2)

	def test_page_list_supports_search_by_title(self):
		response = self.client.get(reverse("page-list"), {"search": "Getting"})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["title"], "Getting Started")

	def test_page_list_honors_ordering_query_param(self):
		response = self.client.get(reverse("page-list"), {"ordering": "created_at"})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		ordered_titles = [item["title"] for item in response.data]
		self.assertEqual(ordered_titles, ["Getting Started", "API Reference"])

	def test_page_list_supports_limit_offset_pagination(self):
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
		response = self.client.get(reverse("page-detail", args=[self.page_1.pk]))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["id"], self.page_1.pk)
		self.assertEqual(response.data["title"], "Getting Started")

	def test_page_detail_returns_404_for_missing_item(self):
		response = self.client.get(reverse("page-detail", args=[99999]))
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
