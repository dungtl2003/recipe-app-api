"""
Tests for the tag API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from recipe.serializers import TagSerializer

from core.models import Tag

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_tag(user, **kwargs):
    """Create and return tag."""
    defaults = {
        'name': 'Sample tag',
        'user': user,
    }
    defaults.update(kwargs)
    return Tag.objects.create(**defaults)


def create_user(**kwargs):
    """Create and return a user."""
    defaults = {
        'email': 'test@example.com',
        'password': 'samplepass123',
    }
    defaults.update(kwargs)
    return get_user_model().objects.create_user(**defaults)


class PublicTagApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        create_tag(user=self.user, name='Sample 1')
        create_tag(user=self.user, name='Sample 2')
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        other_user = create_user(email='user2@example.com')
        wrong_tag = create_tag(user=other_user, name='Sample 1')
        create_tag(user=other_user, name='Sample 2')
        create_tag(user=self.user, name='Sample 3')
        right_tag = create_tag(user=self.user, name='Sample 4')
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tags = Tag.objects.filter(user=self.user).order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(tags.count(), 2)
        self.assertTrue(tags.get(name__contains=right_tag.name))
        self.assertEqual(res.data[0]['id'], right_tag.id)
        self.assertFalse(tags.filter(id=wrong_tag.id).exists())

    def test_update_tag(self):
        """Test updating a tag."""
        tag = create_tag(user=self.user, name='Old name')
        payload = {'name': 'Updated name'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tag.refresh_from_db()
        serializer = TagSerializer(tag)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(tag.name, payload['name'])
