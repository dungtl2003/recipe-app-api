"""
Tests for the tag API.
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from recipe.serializers import TagSerializer
from recipe.utils.create_object import (
    create_tag,
    create_recipe,
    create_user,
)

from core.models import Tag

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])


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

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = create_tag(user=self.user, name='Sample tag')
        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_filter_tags_assigned_to_recipe(self):
        """Test filtering only tags that are assigned to a recipe."""
        tag1 = create_tag(user=self.user, name='Breakfast')
        tag2 = create_tag(user=self.user, name='Lunch')
        tag3 = create_tag(user=self.user, name='Dinner')
        r1 = create_recipe(user=self.user, title='Fried egg')
        r2 = create_recipe(user=self.user, title='Pulled pork bread')
        r1.tags.add(tag1)
        r2.tags.add(tag2)

        params = {'assigned_only': 1}
        res = self.client.get(TAGS_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        s3 = TagSerializer(tag3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags are unique."""
        tag = create_tag(user=self.user, name='Breakfast')
        create_tag(user=self.user, name='Lunch')
        recipe1 = create_recipe(user=self.user, title='Fried egg')
        recipe2 = create_recipe(user=self.user, title='Steak')
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        params = {'assigned_only': 1}
        res = self.client.get(TAGS_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
