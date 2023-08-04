"""
Serializers for the user API View.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
# gettext_lazy should only be used in forms or models because it will only
# need to translate once when django starts.
# on the other hands, gettext should be used in something like view because
# it will be called many times, each time, it needs to make newly executed.
from django.utils.translation import gettext as _

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

    def update(self, instance, validated_data):
        """Updte and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={
            'input_type': 'password',
        },
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
