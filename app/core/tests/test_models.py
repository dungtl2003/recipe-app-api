"""
Tests for models.
"""

# get_user_model will always get the custom user if you have, else get
# default user model. Also, we want to save user in test database, so we will
# use TestCase rather than SimpleTestCase.
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    """Tests models."""

    def test_create_user_with_email_successful(self):
        """Tests creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        # password in user should be hashed, so we can not compare password
        # like email --> use check_password function.
        self.assertTrue(user.check_password(password))
