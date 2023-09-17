"""
Tests for the tags API endpoint.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Return recipe detail URL"""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email="email@here.com", password="testpass123"):
    """Create and return a sample user"""
    return get_user_model().objects.create_user(email, password)


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
    Test authenticated tags API access
    """

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        # Act
        res = self.client.get(TAGS_URL)

        # Assert
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        other_user = create_user(email="bob@here.com", password="passwd")
        Tag.objects.create(user=other_user, name="Fruity")
        tag = Tag.objects.create(user=self.user, name="Comfort Food")

        # Act
        res = self.client.get(TAGS_URL)

        # Assert
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {"name": "Test Tag"}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()
        self.assertTrue(exists)

    def test_update_tag_successful(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user=self.user, name="Test Tag")
        payload = {"name": "New Tag Name"}
        self.client.patch(detail_url(tag.id), payload)

        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag_successful(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name="Test Tag")
        self.client.delete(detail_url(tag.id))

        exists = Tag.objects.filter(
            user=self.user,
            name=tag.name
        ).exists()
        self.assertFalse(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {"name": ""}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
