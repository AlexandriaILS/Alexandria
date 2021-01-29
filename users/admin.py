from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext as _

from users.models import AlexandriaUser


class AlexandriaUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("card_number", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("card_number", "email", "first_name", "last_name", "is_staff")
    search_fields = ("card_number", "first_name", "last_name", "email")
    ordering = ("card_number",)


admin.site.register(AlexandriaUser, AlexandriaUserAdmin)
