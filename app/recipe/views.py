"""
Views for the recipe API.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import (
    viewsets,
    mixins,
    authentication,
    permissions,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import (
    Recipe,
    Tag,
    Ingredient,
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
@extend_schema_view(
    # extend schema for list endpoint.
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API."""
    # most situations beside listing, we want to use RecipeDetailSerializer.
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    # By default, it will return all, but we only want recipes for
    # authenticated user.
    def get_queryset(self):
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def get_serializer_class(self):
        """return the serializer class for request."""
        # if action is list, we return RecipeSerializer.
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        # when creating the recipe, the user attr is missing, so we have to
        # add the current user (the user wants to create recipe) into the
        # recipe and then save the recipe.
        serializer.save(user=self.request.user)

    # detail: a boolean that indicates whether the action applies to a single
    # instance or the whole collection. In this case, detail=True, which means
    # the action requires a primary key argument to identify the instance.

    # url_path: a string that defines the URL path for the action. In this
    # case, it's 'upload-image', which means the action can be accessed at
    # /recipes/{pk}/upload-image/. Note that the path has pk because
    # detail=True. If detail=False, then the path will be
    # /recipes/upload-image/.

    # Normally, the action function takes 1 argument: request. But because
    # detail=True, the action function will also take pk argument.
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        # Get the recipe instance from the database using the pk.
        recipe = self.get_object()
        # This will return RecipeImageSerializer(recipe, data=request.data),
        # which will be converted to serializer object.

        # data: the data will be used to update or create the instance.
        # In this case, data will be used to update recipe.

        # Detail: the recipe has title, price, description, etc. But we want
        # to serializer it into RecipeImageSerializer, which only needs id,
        # image. We also pass the data in to update the recipe object. If
        # the data is valid - serializer is valid, we can save the instance to
        # the database using serializer.save(). If not, then we will not save
        # and return bad request respone.
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Refactoring note: In this viewsets, we should refactor to reduce duplication
# in code. Both tag and ingredient share the same functionality, so we can
# safety make base class for both of them. You may think serializers
# module can be done the same, but although they work the same way, the way
# to implement them are different, so we can not refactor that. As for the
# test module, a lot of functions have the same line of code, but you should
# not refactor them because they don't have any relationship to each other.
# Each test is for different cases, and they don't have the same purpose
# (beside for testing).
# Inconclusion, for now, only good place to refactor is this module.
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='assigned_only',
                type=OpenApiTypes.INT,
                enum=[0, 1],
                description='Filter by items assigned to recipes.',
            )
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """retrieve tags for authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset

        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


# In RecipeViewSet, we extend ModelViewSet because we can perform all CRUD
# operations on recipe. But in TagViewSet, we can not create tag in recipe,
# tag must be created in user to avoid duplication, so we will use mixins.
# Note that we HAVE TO extend all mixin first and then the base class like
# GenericViewSet. Otherwise, it will lose functionalities.
class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
