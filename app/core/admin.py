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

    # in Django, the fieldsets attribute is used to control the layout of
    # the admin pages for EDITING AN OBJECT. That means it helps change and
    # delete object BUT not create. User model must have all attributes in
    # fieldsets.
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

    # The add_fieldsets attribute is used to control the layout of the admin
    # pages for CREATING A NEW OBJECT. That means it only helps create, not
    # change or delete object (oposite of fieldsets). Note that user model
    # does NOT have to have all attributes in add_fieldsets. But the addition
    # field will not be saved to the user model.
    # The 'classes': ('wide') is used to specify the CSS classes. In this
    # case, it specifies that the fieldset should be displayed with a wider
    # width than the default.
    add_fieldsets = (
        (
            None,
            {
                'classes': (
                    'wide',
                ),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'name',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ),
            }
        ),
    )


# You must add the second argument if you want to register the user to
# your custom admin. If you don't have custom admin then the second argument
# is optional.
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
