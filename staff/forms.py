from django import forms
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext as _

from users.models import BranchLocation


class StaffSettingsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = None
        if kwargs.get("request"):
            request = kwargs.pop("request")

        super().__init__(*args, **kwargs)

        if not self.is_bound:
            # only run on GET and not POST
            self.fields["default_branch"].queryset = self.initial[
                "default_branch_queryset"
            ]

        if request:
            # make sure that you can only award permissions that you have yourself
            # (backed with server-side check on submit)
            self.fields["permissions"].queryset = Permission.objects.filter(
                codename__in=[
                    obj.split(".")[1] for obj in request.user.get_all_permissions()
                ]
            ).order_by("content_type__app_label")
            self.fields["permissions"].initial = Permission.objects.filter(
                codename__in=[
                    obj.split(".")[1] for obj in self.initial["permissions_initial"]
                ]
            )

    card_number = forms.CharField()

    title = forms.CharField()

    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    is_minor = forms.BooleanField(label=_("Person is legally a minor"), required=False)
    birth_year = forms.IntegerField(
        label=_("Year of birth"),
        help_text=_(
            "Optional. Used to tell people apart with the same name in a privacy-centric way."
        ),
        required=False,
    )
    notes = forms.CharField(widget=forms.Textarea, required=False)
    default_branch = forms.ModelChoiceField(queryset=BranchLocation.objects.all())

    address_1 = forms.CharField()
    address_2 = forms.CharField(required=False)
    city = forms.CharField()
    state = forms.CharField()
    zip_code = forms.IntegerField()

    is_staff = forms.BooleanField(
        label="Person is employed here",
        help_text=_("Uncheck this to make this account a Patron account."),
        required=False,
    )
    is_active = forms.BooleanField(
        label="Account is active",
        help_text=_("Uncheck this to disable the account entirely."),
        required=False,
    )

    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        help_text=_(
            "You can only modify permissions that you yourself have. If you don't see"
            " what you're looking for, reach out to your manager for assistance."
        ),
        required=False,
    )
