"""
Serializers for the user API View.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers


# ModelSerializer class provides a shortcut that lets you automatically
# create a Serializer class with fields that correspond to the model fields.
# It is liked Serializer class but:
# 1. Automatically generate a set of fields for yo, based on the model.
# 2. Automatically generate validators for serializer.
# 3. Include simple default implementations of .create() and .update()
# https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    # tell framework the model, fields and extra arguments we want to parse
    # to the serializer.
    class Meta:
        # this serializer is for user.
        model = get_user_model()
        # By default, all the model fields on the class will be mapped to the
        # corresponding serializer fields. Use fields if you just want a
        # subset of te default fields to be used in a model serializer.
        # It is strongly recommended, this will make it less likely to result
        # in unintentionally exposing data when your models change.
        fields = ['email', 'password', 'name']
        # provide extra metadata to different fields.
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5
            }
        }

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)
