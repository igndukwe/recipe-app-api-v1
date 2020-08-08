from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# for converting strings in python to human readable format
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    # order by id
    ordering = ['id']
    # list of items to display
    list_display = ['email', 'name']
    fieldsets = (
        # () is refered to as a section in the admin
        # - First part is the section title
        # - while the second part is the fields
        # > None: means no title name
        # > Other sections include: Personal Info, Permissions
        #   and Important dates
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login', )})

    )

    # The add_fieldsets class variable is used to define the fields
    # that will be displayed on the create user page.
    # - The classes key sets any custom CSS
    #   classes we want to apply to the form section.
    # - The fields key sets the fields you wish to display in your form.
    # In this example, the create page
    # will allow you to set an email, password1 and password2

    # Furthermore:
    # This example create a section with no name (as set to None),
    # set a specific width to all the fields by using classes key set
    # and display fields email,password1 and password2 by using key set fields
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
admin.site.register(models.Recipe)
