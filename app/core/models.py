"""
Database models.
"""
# AbstractBaseUser contains functionality for auth system, but not fields,
# PermissionMixin contains functioinality for the permissions and fields
# needed.
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_field):
        """Create, save and return a new user."""
        # self.model() is liked User()
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        # support multiple databases.
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # assign user manager
    objects = UserManager()

    # define field for authentication, default is username, not email.
    USERNAME_FIELD = 'email'
