from django import forms

from users.models import BranchLocation


class StaffSettingsForm(forms.Form):
    card_number = forms.CharField()

    title = forms.CharField()

    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    is_minor = forms.BooleanField()
    birth_year = forms.IntegerField()
    notes = forms.CharField(widget=forms.Textarea)
    default_branch = forms.ModelChoiceField(queryset=BranchLocation.objects.filter())

    address_1 = forms.CharField()
    address_2 = forms.CharField()


    is_staff = forms.BooleanField()
    is_active = forms.BooleanField()
