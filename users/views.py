from django.shortcuts import render, HttpResponseRedirect, reverse
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import ugettext as _

from utils import build_context
from users.forms import LoginForm


class LoginView(View):
    def get(self, request):
        context = build_context({"slim_form": True, "form": LoginForm})
        return render(request, "generic_form.html", context)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                int(data["card_number"])
            except ValueError:
                messages.error(request, _("Card number needs to be an actual number."))
                return HttpResponseRedirect(reverse("login"))

            user = authenticate(
                request, username=data["card_number"], password=data["password"]
            )
            if user:
                login(request, user)
                return HttpResponseRedirect(
                    request.GET.get("next", reverse("homepage"))
                )
            messages.error(request, _("Invalid login information. Try again?"))
            return HttpResponseRedirect(reverse("login"))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get("next", reverse("homepage")))


def profile_settings(request):
    ...


def profile_settings_edit(request):
    ...
