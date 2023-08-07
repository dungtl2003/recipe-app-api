"""
Views for the recipe API.
"""
from rest_framework import viewsets, authentication, permissions

from core.models import Recipe
from recipe import serializers


# we will use viewsets for CRUD api. Otherwise, we use viewAPI like user API.
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API."""
    # most situations beside listing, we want to use RecipeDetailSerializer.
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
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
