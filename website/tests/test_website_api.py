from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from website.models import Website


class WebsiteGETTests(APITestCase):
	'''Tests for GET requests to the Website API endpoints.'''
	@classmethod
	def setUpTestData(cls):
		'''Set up test data for all tests in this class.'''
		user_model = get_user_model()
		cls.user = user_model.objects.create_user(
			username="tester",
			email="tester@example.com",
			password="test-password",
		)

		cls.website_1 = Website.objects.create(
			user=cls.user,
			name="Alpha Site",
			description="First",
			url="https://alpha.example.com",
		)
		cls.website_2 = Website.objects.create(
			user=cls.user,
			name="Beta Site",
			description="Second",
			url="https://beta.example.com",
		)

	def test_website_list_returns_all_results(self):
		'''Test that the website list endpoint returns all items.'''
		response = self.client.get(reverse("website-list"))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 2)

	def test_website_list_supports_search_by_name(self):
		'''Test that the website list endpoint supports searching by name.'''
		response = self.client.get(reverse("website-list"), {"search": "Alpha"})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["name"], "Alpha Site")

	def test_website_list_honors_ordering_query_param(self):
		'''Test that the website list endpoint honors the ordering query parameter.'''
		response = self.client.get(reverse("website-list"), {"ordering": "created_at"})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		ordered_names = [item["name"] for item in response.data]
		self.assertEqual(ordered_names, ["Alpha Site", "Beta Site"])

	def test_website_list_supports_limit_offset_pagination(self):
		'''Test that the website list endpoint supports limit and offset pagination.'''
		first_page = self.client.get(
			reverse("website-list"),
			{"limit": 1, "offset": 0},
		)

		self.assertEqual(first_page.status_code, status.HTTP_200_OK)
		self.assertEqual(first_page.data["count"], 2)
		self.assertIsNone(first_page.data["previous"])
		self.assertIn("limit=1", first_page.data["next"])
		self.assertIn("offset=1", first_page.data["next"])
		self.assertEqual(len(first_page.data["results"]), 1)
		self.assertEqual(first_page.data["results"][0]["name"], "Beta Site")

	def test_website_detail_returns_single_item(self):
		'''Test that the website detail endpoint returns a single item.'''
		response = self.client.get(reverse("website-detail", args=[self.website_1.pk]))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["id"], self.website_1.pk)
		self.assertEqual(response.data["name"], "Alpha Site")

	def test_website_detail_returns_404_for_missing_item(self):
		'''Test that the website detail endpoint returns 404 for a missing item.'''
		response = self.client.get(reverse("website-detail", args=[99999]))
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class WebsitePOSTTests(APITestCase):
	'''Tests for POST requests to the Website API endpoints.'''
	@classmethod
	def setUpTestData(cls):
		'''Set up test data for all tests in this class.'''
		user_model = get_user_model()
		cls.user = user_model.objects.create_user(
			username="tester",
			email="tester@example.com",
			password="test-password",
		)

	def test_create_website_with_valid_data(self):
		'''Test creating a website with valid data.'''
		data = {
			"user": self.user.id,
			"name": "New Site",
			"description": "A new website",
			"url": "https://newsite.example.com",
		}
		response = self.client.post(reverse("website-list"), data)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Website.objects.count(), 1)
		self.assertEqual(response.data["name"], "New Site")
		self.assertEqual(response.data["url"], "https://newsite.example.com")

	def test_create_website_with_missing_required_fields(self):
		'''Test creating a website without required fields fails.'''
		data = {
			"description": "Missing required fields",
		}
		response = self.client.post(reverse("website-list"), data)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Website.objects.count(), 0)

	def test_create_website_with_duplicate_name(self):
		'''Test creating a website with duplicate name fails.'''
		Website.objects.create(
			user=self.user,
			name="Duplicate Name",
			url="https://first.example.com",
		)
		data = {
			"user": self.user.id,
			"name": "Duplicate Name",
			"url": "https://second.example.com",
		}
		response = self.client.post(reverse("website-list"), data)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Website.objects.count(), 1)

	def test_create_website_with_duplicate_url(self):
		'''Test creating a website with duplicate URL fails.'''
		Website.objects.create(
			user=self.user,
			name="First Site",
			url="https://duplicate.example.com",
		)
		data = {
			"user": self.user.id,
			"name": "Second Site",
			"url": "https://duplicate.example.com",
		}
		response = self.client.post(reverse("website-list"), data)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Website.objects.count(), 1)


class WebsitePUTTests(APITestCase):
	'''Tests for PUT requests to the Website API endpoints.'''
	@classmethod
	def setUpTestData(cls):
		'''Set up test data for all tests in this class.'''
		user_model = get_user_model()
		cls.user = user_model.objects.create_user(
			username="tester",
			email="tester@example.com",
			password="test-password",
		)

		cls.website = Website.objects.create(
			user=cls.user,
			name="Original Site",
			description="Original description",
			url="https://original.example.com",
		)

	def test_update_website_with_valid_data(self):
		'''Test updating a website with valid data using PUT.'''
		data = {
			"user": self.user.id,
			"name": "Updated Site",
			"description": "Updated description",
			"url": "https://updated.example.com",
		}
		response = self.client.put(
			reverse("website-detail", args=[self.website.pk]),
			data,
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.website.refresh_from_db()
		self.assertEqual(self.website.name, "Updated Site")
		self.assertEqual(self.website.description, "Updated description")
		self.assertEqual(self.website.url, "https://updated.example.com")

	def test_update_website_with_missing_required_fields(self):
		'''Test updating a website with missing required fields fails.'''
		data = {
			"description": "Only description",
		}
		response = self.client.put(
			reverse("website-detail", args=[self.website.pk]),
			data,
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_update_nonexistent_website(self):
		'''Test updating a nonexistent website returns 404.'''
		data = {
			"user": self.user.id,
			"name": "Updated Site",
			"url": "https://updated.example.com",
		}
		response = self.client.put(
			reverse("website-detail", args=[99999]),
			data,
		)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class WebsitePATCHTests(APITestCase):
	'''Tests for PATCH requests to the Website API endpoints.'''
	@classmethod
	def setUpTestData(cls):
		'''Set up test data for all tests in this class.'''
		user_model = get_user_model()
		cls.user = user_model.objects.create_user(
			username="tester",
			email="tester@example.com",
			password="test-password",
		)

		cls.website = Website.objects.create(
			user=cls.user,
			name="Original Site",
			description="Original description",
			url="https://original.example.com",
		)

	def test_partial_update_website_name(self):
		'''Test partially updating a website's name using PATCH.'''
		data = {
			"name": "Partially Updated Site",
		}
		response = self.client.patch(
			reverse("website-detail", args=[self.website.pk]),
			data,
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.website.refresh_from_db()
		self.assertEqual(self.website.name, "Partially Updated Site")
		self.assertEqual(self.website.description, "Original description")
		self.assertEqual(self.website.url, "https://original.example.com")

	def test_partial_update_nonexistent_website(self):
		'''Test partially updating a nonexistent website returns 404.'''
		data = {
			"name": "Updated Site",
		}
		response = self.client.patch(
			reverse("website-detail", args=[99999]),
			data,
		)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class WebsiteDELETETests(APITestCase):
	'''Tests for DELETE requests to the Website API endpoints.'''
	@classmethod
	def setUpTestData(cls):
		'''Set up test data for all tests in this class.'''
		user_model = get_user_model()
		cls.user = user_model.objects.create_user(
			username="tester",
			email="tester@example.com",
			password="test-password",
		)

	def test_delete_website(self):
		'''Test deleting a website.'''
		website = Website.objects.create(
			user=self.user,
			name="Site to Delete",
			url="https://delete.example.com",
		)
		response = self.client.delete(reverse("website-detail", args=[website.pk]))

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(Website.objects.count(), 0)

	def test_delete_nonexistent_website(self):
		'''Test deleting a nonexistent website returns 404.'''
		response = self.client.delete(reverse("website-detail", args=[99999]))

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


