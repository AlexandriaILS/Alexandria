from django import forms


class LoCSearchForm(forms.Form):
    search_term = forms.CharField(max_length=200)
    store = forms.BooleanField(required=False)


class LoginForm(forms.Form):
    card_number = forms.IntegerField()
    password = forms.CharField(widget=forms.PasswordInput)
