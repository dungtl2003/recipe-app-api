"""
Tests for models.
"""

# get_user_model will always get the custom user if you have, else get
# default user model. Also, we want to save user in test database, so we will
# use TestCase rather than SimpleTestCase.
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from .. import models


def create_user(**kwargs):
    defaults = {
        'email': 'test@example.com',
        'password': 'testpass123',
    }
    defaults.update(kwargs)
    return get_user_model().objects.create_user(**defaults)


class ModelTest(TestCase):
    """Tests models."""

    def test_create_user_with_email_successful(self):
        """Tests creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        # password in user should be hashed, so we can not compare password
        # like email --> use check_password function.
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Tests email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.com', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = create_user(email=email)
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError"""
        # with = try - finally
        with self.assertRaises(ValueError):
            create_user(email='')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com', 'sample123')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = create_user()
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description.',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test create and return a tag."""
        user = create_user()
        tag = models.Tag.objects.create(
            name='Sample tag',
            user=user,
        )

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test create and return an ingredient."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(user=user, name='Sample')

        self.assertEqual(str(ingredient), ingredient.name)

    # uuid: unique identifier for the file we want to upload. This will
    # ensure each file will have the unique name.
    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        # This function is supposed to generate the path to the image that
        # will be uploaded.
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
