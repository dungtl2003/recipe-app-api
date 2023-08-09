"""
Test for recipe api.
"""
from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'https://example.com/recipe.pdf',
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def create_user(**kwargs):
    """Create and return a new user."""
    defaults = {
        'email': 'test@example.com',
        'password': '123456a@',
    }
    defaults.update(kwargs)
    return get_user_model().objects.create_user(**defaults)


def image_upload_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='123456a@'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retriving a list of recipes."""
        create_recipe(self.user)
        create_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        # -id: return in reverse order.
        recipes = Recipe.objects.all().order_by('-id')
        # many=True: normally, by default, serializer will expect argument
        # as a single object. By turn on this option, serializer will
        # expect the argument as a list of objects.
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # In the test above, we don't actually know if all recipes are belong to
    # that user or not. So we need another test to check this.
    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = create_user(
            email='other@example.com',
            password='testpass123'
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'recipe title',
            'time_minutes': 30,
            'price': Decimal('5.99'),
            'description': 'test creating recipe',
            'link': 'https://testlink.com',
        }
        res = self.client.post(path=RECIPES_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )

        payload = {
            'title': 'New recipe title',
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of a recipe."""
        original = {
            'user': self.user,
            'title': 'Sample title',
            'price': Decimal('9.99'),
            'time_minutes': 12,
            'link': 'https://example.com/recipe.pdf',
        }
        recipe = create_recipe(**original)

        payload = {
            'user': self.user,
            'title': 'New title',
            'price': Decimal('69.99'),
            'time_minutes': 15,
            'description': 'It has description now!',
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.link, original['link'])

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(
            email='new_user@example.com',
            password='passexample123',
        )
        recipe = create_recipe(
            user=self.user,
        )
        payload = {
            'user': new_user,
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(
            user=self.user,
        )
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete other user recipe error."""
        new_user = create_user(
            email='new_user@example.com',
            password='123456a@',
        )
        recipe = create_recipe(
            user=new_user,
        )
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'That Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tags."""
        tag = Tag.objects.create(user=self.user, name='Tag 1')
        payload = {
            'title': 'Sample title',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Tag 1'}, {'name': 'Tag 2'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        tags = Tag.objects.all()

        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating tag when updating a recipe."""
        recipe = create_recipe(user=self.user)
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_tag = Tag.objects.get(
            user=self.user,
            name=payload['tags'][0]['name'],
        )

        # No need to refresh recipe from the db because Django will
        # automatically update the many-to-many relationship when
        # you use the methods on the related manager. In this case,
        # the patch() method only adds and removes tags from the recipe.
        # Therefore, recipe.tags.all() will reflect the latest changes
        # without reloadin gthe recipe object.
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipe tags."""
        tag_1 = Tag.objects.create(user=self.user, name='Tag 1')
        tag_2 = Tag.objects.create(user=self.user, name='Tag 2')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_1)
        recipe.tags.add(tag_2)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)
        self.assertEqual(Tag.objects.count(), 2)
        self.assertIn(tag_1, Tag.objects.all())
        self.assertIn(tag_2, Tag.objects.all())

    def test_patch_recipe_without_affect_tags(self):
        """Test patch recipe fields except tags field."""
        recipe = create_recipe(user=self.user)
        tag_1 = Tag.objects.create(user=self.user, name='Sample tag 1')
        tag_2 = Tag.objects.create(user=self.user, name='Sample tag 2')
        recipe.tags.add(tag_1)
        recipe.tags.add(tag_2)

        payload = {
            'title': 'Updated title',
            'minutes': 69,
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_1, recipe.tags.all())
        self.assertIn(tag_2, recipe.tags.all())

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a new recipe with new ingredients."""
        payload = {
            'title': 'Fried egg',
            'time_minutes': 20,
            'price': Decimal('10.99'),
            'ingredients': [
                {'name': 'Salt'},
                {'name': 'Pepple'},
                {'name': 'Egg'},
            ]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(title=payload['title'])

        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), len(payload['ingredients']))
        for ingredient in payload['ingredients']:
            exists = ingredients.filter(name=ingredient['name']).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """Test creating recipe with existing ingredients."""
        salt = Ingredient.objects.create(
            user=self.user,
            name='Salt',
        )
        payload = {
            'title': 'Sample title',
            'time_minutes': 12,
            'price': Decimal('4.99'),
            'ingredients': [
                {'name': 'Salt'},
                {'name': 'Pepple'},
                {'name': 'Egg'},
            ]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(title=payload['title'])

        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        ingredients = recipe.ingredients.all()

        self.assertIn(salt, ingredients)
        for ingredient in payload['ingredients']:
            exists = ingredients.filter(name=ingredient['name']).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating ingredients when updating a recipe."""
        recipe = create_recipe(self.user)
        payload = {
            'ingredients': [
                {'name': 'chicken'},
                {'name': 'ham'},
                {'name': 'bread'},
            ]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = (Ingredient
                       .objects
                       .all()
                       .order_by('-name'))

        self.assertEqual(ingredients.count(), len(payload['ingredients']))
        for ingredient in ingredients:
            exists = recipe.ingredients.filter(id=ingredient.id).exists()
            self.assertTrue(exists)

    def test_update_recipe_assign_ingredient(self):
        """Test assigning existing ingredients when updating a recipe."""
        salt = Ingredient.objects.create(
            user=self.user,
            name='Salt',
        )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(salt)

        pepple = Ingredient.objects.create(
            user=self.user,
            name='Pepple',
        )
        payload = {'ingredients': [{'name': 'Pepple'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(pepple, recipe.ingredients.all())
        self.assertNotIn(salt, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing a recipe ingredients."""
        ingredient = Ingredient.objects.create(
            user=self.user, name='Garlic'
        )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {'ingredients': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_update_recipe_except_ingredients_field(self):
        """Test updating recipe except for the ingredients."""
        recipe = create_recipe(user=self.user)
        salt = Ingredient.objects.create(user=self.user, name='Salt')
        pepple = Ingredient.objects.create(user=self.user, name='Pepple')
        recipe.ingredients.add(salt)
        recipe.ingredients.add(pepple)

        payload = {
            'title': 'Updated title',
            'price': Decimal('69.99'),
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(salt, recipe.ingredients.all())
        self.assertIn(pepple, recipe.ingredients.all())


class ImageUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(self.user)

    # This will run after every test, oposite to setUp() method.
    # Because we don't want to save test images in our machine.
    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe."""
        url = image_upload_url(self.recipe.id)
        # There will be 2 images files. One is image_file, which is the image
        # file that the user want to upload. When they upload that image, there
        # will be a new image file, a stored version of image_file on the
        # server.

        # with statement is liked try-finally. It will create a temp file
        # and when all code within this statement is done, then the temp file
        # will be closed. And by default, the temp file when closed will be
        # automatically deleted.

        # .jpg is a file extension used for image files that are compressed
        # using the JPEG (Joint Photographic Experts Group) standard. JPEG
        # is a lossy compression algorithm, which means that some image
        # quality is sacrificed to reduce the file size. The .jpg extension
        # is widely used for photographs and Internet graphics, and can be
        # opend by most image viewers and editors.
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            # Create a new image with RGB color mode with 10x10 px.

            # RGB color mode is a way of representing colors using the
            # combination of Red, Green and Blue light. It is an additive
            # color model, which means that adding more light increases the
            # brightness and creates lighter colors. RGB color mode is used
            # for digital devices, such as monitors, phones and TVs. However,
            # the xact shades of RGB colors may vary depending on the device
            # and its settings.
            img = Image.new('RGB', (10, 10))
            # Saving the image to the image_file. Once that done, the pointer
            # will be on the end of the file. This will save the image as a
            # JPEG file, which is a common format that uses lossy compression
            # to reduce the file size.
            img.save(image_file, format='JPEG')
            # Seek back to the begining of the file. So the file can be read
            # by other functions.
            image_file.seek(0)
            payload = {'image': image_file}
            # This format argument specifies the content type of the request
            # body. Multipart format will be used in case you want to send
            # multiple types of data in a single request, such as files, text
            # fields, JSON data, etc. Multipart format allows you to separate
            # each part of data by a boundary and specify its content type
            # and name. This way, the server can process each part of data
            # accordingly.

            # We will upload this image using multipart form. This is the best
            # way to upload image on django.
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        # Once the image file is uploaded by the user, there must be a stored
        # version of it in the server, aka this system. This code is to check
        # that.
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image."""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
