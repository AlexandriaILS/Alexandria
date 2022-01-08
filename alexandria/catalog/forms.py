from django import forms
from django.utils.translation import gettext as _

from alexandria.users.models import User, USLocation


class LoginForm(forms.Form):
    card_number = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class PatronSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            self.fields["last_name"].widget.attrs["disabled"] = True
            self.fields["card_number"].widget.attrs["disabled"] = True
            self.fields["formatted_address"].widget.attrs["disabled"] = True

            self.fields["card_number"].required = False

            self.fields["formatted_address"].help_text = _(
                "If you need to change this, please bring updated proof of address"
                " to any branch."
            )

            self.fields["formatted_address"].label = USLocation._meta.get_field(
                "address_1"
            ).verbose_name

            addr_string = instance.address.address_1
            if instance.address.address_2:
                addr_string += f", {instance.address.address_2}"
            addr_string += f", {instance.address.city} {instance.address.zip_code}"
            self.fields["formatted_address"].initial = addr_string

            self.fields["default_branch"].queryset = instance.get_branches()
            # make it so that we don't have the blank entry at the top
            self.fields["default_branch"].empty_label = None

            self.fields["last_name"].help_text = _(
                "If you need to change this, please bring updated ID with you"
                " to any branch."
            )

    formatted_address = forms.CharField()

    def _get_readonly_value(self, value):
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            return getattr(instance, value)
        else:
            return self.cleaned_data[value]

    def clean_last_name(self):
        # make sure that we don't overwrite their last name; needs to be
        # done by staff
        return self._get_readonly_value("last_name")

    def clean_card_number(self):
        return self._get_readonly_value("card_number")

    class Meta:
        model = User
        fields = [
            "card_number",
            "first_name",
            "last_name",
            "email",
            "formatted_address",
            "default_branch",
        ]
