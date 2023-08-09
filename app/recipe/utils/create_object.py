"""
Create and return an object to test.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)


def create_tag(user, **kwargs):
    """Create and return a tag."""
    defaults = {
        'user': user,
        'name': 'Sample tag',
    }
    defaults.update(kwargs)
    return Tag.objects.create(**defaults)


def create_ingredient(user, **kwargs):
    """Create and return an ingredient."""
    defaults = {
        'user': user,
        'name': 'Sample ingredient',
    }
    defaults.update(kwargs)
    return Ingredient.objects.create(**defaults)


def create_recipe(user, **kwargs):
    """Create and return a recipe."""
    defaults = {
        'user': user,
        'title': 'Sample recipe',
        'time_minutes': 15,
        'price': Decimal('6.99'),
        'link': 'https://example.com',
        'description': 'This is a description',
    }
    defaults.update(kwargs)
    return Recipe.objects.create(**defaults)


def create_user(**kwargs):
    """Create and return a user."""
    defaults = {
        'email': 'test@example.com',
        'password': 'testpass123',
    }
    defaults.update(kwargs)

    if defaults.get('is_super'):
        return get_user_model().objects.create_super_user(**defaults)

    return get_user_model().objects.create_user(**defaults)
