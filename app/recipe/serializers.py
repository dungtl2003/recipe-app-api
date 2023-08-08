"""
Serializers for recipe API.
"""
from rest_framework import serializers
from core.models import (
    Recipe,
    Tag,
    Ingredient,
)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient view."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes',
                  'price', 'link', 'tags', 'ingredients']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        # self.context['request'] will return rest_framework.request.Request.
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context['request'].user

        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    # By default, tags field is read-only. Also, we can not add a tag object
    # into recipe object because recipe object only contains relationship with
    # tag, not object. Therefore, we have to override the behavior of creating
    # a new recipe (we want the recipe is created with tags, if tag is existed
    # then we want to reuse that, otherwise we create a new tag).
    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    # When creating new recipe, we can set tags to [] when the user doesn't
    # give tags, otherwise add tags to recipe. But when updating, if the user
    # doesn't give tags field, it can be because the user doesn't want to
    # patch the tags field. So we can not set tags to [] like creating. We
    # have to consider 2 cases, when tags is None then we skip the tags attr,
    # otherwise we add tags like when we create recipe.
    def update(self, instance, validated_data):
        """Update a recipe."""
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
