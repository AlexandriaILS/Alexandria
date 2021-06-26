from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.admin.forms import AdminAuthenticationForm
from django.utils.translation import ugettext as _

from users.models import AlexandriaUser, BranchLocation, USLocation

class AdminSiteLoginForm(AdminAuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': _(
            "Please enter the correct %(username)s and password for a superuser "
            "account. Note that both fields may be case-sensitive."
        ),
    }
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_superuser:
            raise ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )

admin.autodiscover()
# make it so that only superusers can log in instead of the normal `is_staff` flag
admin.site.login_form = AdminSiteLoginForm

class AlexandriaUserCreationForm(UserCreationForm):
    class Meta:
        model = AlexandriaUser
        fields = ("card_number",)
        field_classes = {'card_number': forms.CharField}


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
                    "is_manager",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('card_number', 'password1', 'password2'),
        }),
    )
    list_display = ("card_number", "email", "first_name", "last_name", "is_staff")
    search_fields = ("card_number", "first_name", "last_name", "email")
    ordering = ("card_number",)
    add_form = AlexandriaUserCreationForm


admin.site.register(AlexandriaUser, AlexandriaUserAdmin)
admin.site.register(BranchLocation)
admin.site.register(USLocation)
