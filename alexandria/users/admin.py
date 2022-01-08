from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _

from alexandria.users.models import User, BranchLocation, USLocation
from alexandria.catalog.authentication.views import LoginView

admin.autodiscover()
admin.site.login = LoginView.as_view()


def has_superuser_permission(request):
    # https://stackoverflow.com/a/65955373
    return request.user.is_active and request.user.is_superuser


# Only active superuser can access root admin site (default)
admin.site.has_permission = has_superuser_permission


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("card_number",)
        field_classes = {"card_number": forms.CharField}


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("card_number", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "title",
                    "email",
                    "default_branch",
                    "address",
                    "notes",
                )
            },
        ),
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
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("card_number", "password1", "password2"),
            },
        ),
    )
    list_display = ("card_number", "email", "first_name", "last_name", "is_staff")
    search_fields = ("card_number", "first_name", "last_name", "email")
    ordering = ("card_number",)
    add_form = CustomUserCreationForm
    exclude = User().get_searchable_field_names()


admin.site.register(User, CustomUserAdmin)
admin.site.register(BranchLocation)
admin.site.register(USLocation)
