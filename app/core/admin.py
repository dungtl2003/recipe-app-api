"""
Django admin customization.
"""
# gettext_lazy: automatically translate text to the language you want.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    # order by id
    # the list will only display email and name
    ordering = ['id']
    list_display = ['email', 'name']
    # fieldset is a tuple, inside it contains more tuple/sub tuple,
    # each sub tuple contains a title and a field dict. The first one
    # doesn't have title --> None. If a set has a title, it should be in
    # translate function in case you want to have multiple languages in your
    # project. We have to override the fieldsets in order to use custom user.
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'password',
                )
            }
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (
            _('Important dates'),
            {
                'fields': (
                    'last_login',
                )
            }
        )
    )

    readonly_fields = ['last_login']


# You must add the second argument if you want to register the user to
# your custom admin. If you don't have custom admin then the second argument
# is optional.
admin.site.register(models.User, UserAdmin)
