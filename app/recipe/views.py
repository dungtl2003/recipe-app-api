"""
Views for the recipe API.
"""
from rest_framework import (
    viewsets,
    mixins,
    authentication,
    permissions,
)

from core.models import (
    Recipe,
    Tag,
)

from recipe import serializers
# DRF is a toolkit built on top of the Django web framework that reduces
# the amount of code you need to write to create REST interfaces.

# Views in DRF are used to define the API endpoints. REST framework provides
# an APIView class, which subclasses Django's View class. APIView classes are
# different from regular View classes in the following ways: Requests passed
# to the handler methods will be REST framework's Request instances, not
# Django's HttpRequest instances.

# Generic views are a set of pre-build class-based views that provide basic
# functionalities such as list and detail views. They are built by combining
# GenericAPIView with 1 or more mixin classes.

# Mixins are classes that provide functionality that can be reused by other
# classes. They are used to add common methods to multiple views. Mixins can
# be used wit generic views to add extra functionality.

# ViewSet is an abstraction over APIView which provides actions as method such
# as list (read only, returns multiple resources), retrieve (read only, returns
# single resource), create (write only), update (write only), partial_update
# (write only) and destroy (write only)

# get function will be determited by action. If action is 'list' then
# get_queryset() function will be called. If action is 'retrieve' then
# get_object() function will be called. If you don't override the get_object()
# function then get_object() function will also call get_queryset() function.
# That is the reason why when you don't override any function then getting a
# list will only evoke get_queryset() function while getting an object will
# evoke both get function.


# both APIView and ViewSet are used for building APIs.
# the main difference between them is an APIView can handle SINGLE HTTP
# request, while a ViewSet can handle MULTIPLE HTTP requests. for that reason,
# we will use viewsets for CRUD api. Otherwise, we use viewAPI like user API.
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API."""
    # most situations beside listing, we want to use RecipeDetailSerializer.
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # By default, it will return all, but we only want recipes for
    # authenticated user.
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """return the serializer class for request."""
        # if action is list, we return RecipeSerializer.
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        # when creating the recipe, the user attr is missing, so we have to
        # add the current user (the user wants to create recipe) into the
        # recipe and then save the recipe.
        serializer.save(user=self.request.user)


# In RecipeViewSet, we extend ModelViewSet because we can perform all CRUD
# operations on recipe. But in TagViewSet, we can not create tag in recipe,
# tag must be created in user to avoid duplication, so we will use mixins.
# Note that we HAVE TO extend all mixin first and then the base class like
# GenericViewSet. Otherwise, it will lose functionalities.
class TagViewSet(mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """retrieve tags for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')
