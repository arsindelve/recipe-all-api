"""
Tests for the tags API endpoint.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase
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


class PublicTagsApiTests(SimpleTestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

