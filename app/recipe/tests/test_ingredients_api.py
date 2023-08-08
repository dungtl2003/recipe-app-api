"""
Test for the ingredient API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


def create_user(**kwargs):
    defaults = {
        'email': 'test@example.com',
        'password': '123456a@',
    }
    defaults.update(kwargs)
    return get_user_model().objects.create_user(**defaults)


class PublicIngredientAPITest(TestCase):
    """Test unauthenticated API requests."""
    def test_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        self.client = APIClient()
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_listing_ingredients_successfully(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Sait')
        Ingredient.objects.create(user=self.user, name='Pepple')
        res = self.client.get(INGREDIENT_URL)

        self.assertTrue(res.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test ingredients is belonged to user."""
        other_user = create_user(email='other@example.com')
        right_ingredient = Ingredient.objects.create(
            user=self.user,
            name='Right ingredient',
        )
        wrong_ingredient = Ingredient.objects.create(
            user=other_user,
            name='Wrong ingredient',
        )
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = (Ingredient
                       .objects
                       .filter(user=self.user)
                       .order_by('-name'))
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(ingredients.count(), 1)
        self.assertIn(right_ingredient, ingredients.all())
        self.assertNotIn(wrong_ingredient, ingredients.all())
        self.assertEqual(res.data, serializer.data)
