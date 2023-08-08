"""
Views for the user API.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    # we will use token authentication.
    authentication_classes = [authentication.TokenAuthentication]
    # the user must have authenticated to use this.
    permission_classes = [permissions.IsAuthenticated]

    # we only want to get or update 1 user - current user, so we will use
    # RetrieveUpdateAPIView, which will concrete view for retrieving,
    # updating a model instance, and we also don't need to override
    # get_queryset() method or assign value to queryset. But by default,
    # get_object() method will call get_queryset() method, and because
    # queryset by default will be None, so it will raise exeption.
    # Even if we handle the queryset (which is not correct by logic), we still
    # get exeption because by default, the lookup_field is 'pk' and we want to
    # get the current user, the url will not have 'pk'. So we have to override
    # the get_object() method.
    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
