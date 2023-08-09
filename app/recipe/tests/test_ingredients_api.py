"""
Test for the ingredient API.
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

from recipe.serializers import IngredientSerializer
from recipe.utils.create_object import (
    create_recipe,
    create_ingredient,
    create_user,
)

INGREDIENT_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return an ingredient detail URL."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


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
        create_ingredient(user=self.user, name='Sait')
        create_ingredient(user=self.user, name='Pepple')
        res = self.client.get(INGREDIENT_URL)

        self.assertTrue(res.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test ingredients is belonged to user."""
        other_user = create_user(email='other@example.com')
        right_ingredient = create_ingredient(
            user=self.user,
            name='Right ingredient',
        )
        wrong_ingredient = create_ingredient(
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

    def test_update_ingredient(self):
        """Test updating ingredient successful."""
        original_name = 'Salt'
        ingredient = create_ingredient(
            user=self.user,
            name=original_name,
        )
        payload = {'name': 'Pepple'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()

        self.assertEqual(ingredient.name, payload['name'])
        self.assertEqual(ingredient.user, self.user)

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = create_ingredient(
            user=self.user,
            name='Salt',
        )
        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())

    def test_filter_ingredients_assigned_to_recipe(self):
        """Test filtering only ingredients that are assigned in recipes."""
        i1 = create_ingredient(user=self.user, name='Pepple')
        i2 = create_ingredient(user=self.user, name='Milk')
        i3 = create_ingredient(user=self.user, name='Egg')
        i4 = create_ingredient(user=self.user, name='Salt')
        r1 = create_recipe(user=self.user, title='Steak')
        r2 = create_recipe(user=self.user, title='Milk shake')
        r1.ingredients.add(i1)
        r1.ingredients.add(i4)
        r2.ingredients.add(i2)

        params = {'assigned_only': 1}
        res = self.client.get(INGREDIENT_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        s1 = IngredientSerializer(i1)
        s2 = IngredientSerializer(i2)
        s3 = IngredientSerializer(i3)
        s4 = IngredientSerializer(i4)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)
        self.assertIn(s4.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients return a unique list."""
        ingredient = create_ingredient(user=self.user, name='Eggs')
        create_ingredient(user=self.user, name='Lentils')
        recipe1 = create_recipe(user=self.user, title='Eggs Benedict')
        recipe2 = create_recipe(user=self.user, title='Herb Eggs')
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        params = {'assigned_only': 1}
        res = self.client.get(INGREDIENT_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
