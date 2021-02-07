from django import forms


class LoCSearchForm(forms.Form):
    search_term = forms.CharField(max_length=200)
    store = forms.BooleanField(required=False)
