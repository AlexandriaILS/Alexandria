from django.shortcuts import render, HttpResponseRedirect, reverse
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.db.models import Q

from utils import build_context
from users.forms import LoginForm

from catalog.models import Item
from holds.models import Hold
from utils.views import next_or_reverse


class LoginView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = build_context({"slim_form": True, "form": LoginForm})
        return render(request, "generic_form.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                int(data["card_number"])
            except ValueError:
                messages.error(
                    request, _("Card number needs to be the number on your card.")
                )
                return HttpResponseRedirect(next_or_reverse(request, "login"))

            user = authenticate(
                request, username=data["card_number"], password=data["password"]
            )
            if user and user.host == request.host:
                login(request, user)
                return HttpResponseRedirect(next_or_reverse(request, "homepage"))
            messages.error(request, _("Invalid login information. Try again?"))
            return HttpResponseRedirect(next_or_reverse(request, "login"))


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return HttpResponseRedirect(next_or_reverse(request, "homepage"))


def profile_settings(request: HttpRequest) -> HttpResponse:
    ...


def profile_settings_edit(request: HttpRequest) -> HttpResponse:
    ...


@login_required()
def my_checkouts(request: HttpRequest) -> HttpResponse:
    # todo: finish next
    # https://stackoverflow.com/a/36166644
    # Item.objects.filter(Q(user_checked_out_to__isnull=False) | Q(branch_checked_out_to__isnull=False))
    my_materials = Item.objects.filter(user_checked_out_to=request.user)
    return render(
        request, "user/my_checked_out.html", build_context({"checkouts": my_materials})
    )


@login_required()
def my_holds(request: HttpRequest) -> HttpResponse:
    # todo: finish next
    my_holds = Hold.objects.filter(placed_by=request.user)
    return render(request, "user/my_holds.html", build_context({"checkouts": my_holds}))


@login_required()
def my_fees(request: HttpRequest) -> HttpResponse:
    # todo: finish next
    my_materials = Item.objects.filter(user_checked_out_to=request.user)
    return render(
        request, "user/my_fees.html", build_context({"checkouts": my_materials})
    )
