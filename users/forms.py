from django import forms


class LoginForm(forms.Form):
    card_number = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
