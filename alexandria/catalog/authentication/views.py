from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.generic import View

from alexandria.catalog.forms import LoginForm
from alexandria.utils.views import next_or_reverse, redirect_with_qsps


class LoginView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {"slim_form": True, "form": LoginForm, "show_password_reset": True}
        return render(request, "generic_form.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            user = authenticate(
                request, username=data["card_number"], password=data["password"]
            )
            if user and user.host == request.host:
                login(request, user)
                return redirect(next_or_reverse(request, "homepage"))
        messages.error(request, _("Invalid login information. Try again?"))
        return redirect_with_qsps(request, "login")


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(next_or_reverse(request, "homepage"))
