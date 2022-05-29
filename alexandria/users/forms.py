from django import forms
from django.contrib.auth.models import Permission
from django.utils.translation import gettext as _

from alexandria.users.models import BranchLocation


class PatronForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.is_bound:
            # only run on GET and not POST
            self.fields["default_branch"].queryset = self.initial[
                "default_branch_queryset"
            ]
            if default_account_type_qs := self.initial.get(
                "default_account_type_queryset"
            ):
                # only create the account_type field if the person requesting the form
                # has permissions to see it.
                self.fields["account_type"] = forms.ModelChoiceField(
                    queryset=default_account_type_qs
                )

        # force specific field order
        self.order_fields(
            [
                "card_number",
                "first_name",
                "chosen_first_name",
                "last_name",
                "title",
                "account_type",
                "email",
                "is_minor",
                "birth_year",
                "notes",
                "default_branch",
                "work_branch",
                "address_1",
                "address_2",
                "city",
                "state",
                "zip_code",
            ]
        )

    card_number = forms.CharField()
    first_name = forms.CharField()
    chosen_first_name = forms.CharField()
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
    # this queryset is replaced
    default_branch = forms.ModelChoiceField(
        queryset=BranchLocation.objects.all(),
        help_text=_("Where does this person want their holds to default to?"),
    )

    address_1 = forms.CharField()
    address_2 = forms.CharField(required=False)
    city = forms.CharField()
    state = forms.CharField()
    zip_code = forms.IntegerField()


class PatronEditForm(PatronForm):
    is_active = forms.BooleanField(
        label="Account is active",
        help_text=_("Uncheck this to disable the account entirely."),
        required=False,
    )


class StaffSettingsForm(PatronForm):
    def __init__(self, *args, **kwargs):
        request = None
        if kwargs.get("request"):
            request = kwargs.pop("request")

        super().__init__(*args, **kwargs)

        if request:
            self.fields["work_branch"].queryset = request.user.get_branches()
            self.fields["work_branch"].initial = self.initial["work_branch"]

    title = forms.CharField()
    work_branch = forms.ModelChoiceField(
        queryset=BranchLocation.objects.all(),
        help_text=_("Which branch is this person based out of?"),
    )


class AccountTypeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = None
        if kwargs.get("request"):
            request = kwargs.pop("request")

        super().__init__(*args, **kwargs)

        if request:
            # make sure that you can only award permissions that you have yourself
            # (backed with server-side check on submit)
            self.fields["permissions"].queryset = Permission.objects.filter(
                codename__in=[
                    obj.split(".")[1]
                    for obj in request.user.account_type.get_all_permissions()
                ]
            ).order_by("content_type__app_label")
            self.fields["permissions"].initial = Permission.objects.filter(
                codename__in=[
                    obj.split(".")[1] for obj in self.initial["permissions_initial"]
                ]
            )

    name = forms.CharField(max_length=150)
    # TODO: support itemtype hold and checkout limits in this form
    checkout_limit = forms.IntegerField(
        help_text=_(
            "How many materials total is this account type allowed to have checked out?"
            " Set to zero to disable checkouts entirely for this account type."
        )
    )
    hold_limit = forms.IntegerField(
        help_text=_(
            "How many active holds is this account type allowed to have?"
            " Set to zero to disable holds entirely for this account type."
        )
    )
    # TODO: support allowed_item_types
    can_checkout_materials = forms.BooleanField(
        help_text=_("Is this account type allowed to check out materials at all?")
    )

    is_staff = forms.BooleanField(
        label=_("Employee Group"),
        help_text=_(
            "If checked, this is treated as a staff group with staff permissions."
        ),
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
