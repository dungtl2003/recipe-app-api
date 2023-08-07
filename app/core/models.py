"""
Database models.
"""
# AbstractBaseUser contains functionality for auth system, but not fields,
# PermissionMixin contains functioinality for the permissions and fields
# needed.
from django.conf import settings
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
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        # support multiple databases.
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None):
        """Create, save and return a new superuser."""
        superuser = self.create_user(email, password)
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save(using=self._db)

        return superuser


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


class Recipe(models.Model):
    """Recipe object."""
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    # blank=True: this field will not be required when the form is submitted.
    description = models.TextField(blank=True)
    # link to the recipe.
    link = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title
