from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.generic import View

from alexandria.catalog.forms import PatronSettingsForm
from alexandria.records.models import Hold, Item


@login_required()
def my_checkouts(request: HttpRequest) -> HttpResponse:
    my_materials = Item.objects.filter(user_checked_out_to=request.user).order_by(
        "due_date"
    )
    return render(request, "user/my_checked_out.html", {"checkouts": my_materials})


@login_required()
def my_holds(request: HttpRequest) -> HttpResponse:
    my_holds = Hold.objects.filter(placed_for=request.user, host=request.host)
    return render(request, "user/my_holds.html", {"holds": my_holds})


@login_required()
def my_fees(request: HttpRequest) -> HttpResponse:
    # TODO: Finish after building staff side
    my_fees = ...
    return render(request, "user/my_fees.html", {"fees": my_fees})


class SettingsView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "slim_form": True,
            "form": PatronSettingsForm(instance=request.user),
            "show_password_reset": True,
        }

        context.update({"header": _("My Settings")})
        return render(request, "generic_form.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = PatronSettingsForm(request.POST, instance=request.user)
        fields = form.fields
        form.fields = {i: fields[i] for i in fields if i != "formatted_address"}
        if form.is_valid():
            form.save()
            messages.success(request, _("Your settings were updated!"))
            return redirect("my_settings")
