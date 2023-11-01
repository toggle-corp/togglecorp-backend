from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    User,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    search_fields = ('email', 'first_name', 'last_name',)
    fieldsets = (
        (None, {
            'fields': (
                'email',
                'password'
            )
        }),
        (_('Personal info'), {
            'fields': (
                'first_name',
                'last_name',
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'date_joined',
            )
        }),
        (_('Misc'), {
            'fields': (
                'email_opt_outs',
            )
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': (
                'wide',
            ),
            'fields': (
                'email',
                'password1',
                'password2',
            ),
        }),
    )

    ordering = list_display = (
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
    )
