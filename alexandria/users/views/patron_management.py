from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models.expressions import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from alexandria.catalog.helpers import get_results_per_page
from alexandria.records.models import Hold
from alexandria.users.forms import PatronForm, PatronEditForm
from alexandria.users.models import User, USLocation
from alexandria.searchablefields.strings import clean_text


@csrf_exempt
@permission_required("users.read_patron_account")
def patron_management(request):
    results = request.user.get_modifiable_patrons()
    if search_text := request.POST.get("search_text"):
        search_text = clean_text(search_text)
        for word in search_text.split():
            results = results.filter(
                Q(searchable_first_name__icontains=word)
                | Q(searchable_last_name__icontains=word)
                | Q(title__icontains=word)
                | Q(card_number__icontains=word)
            )

    results_per_page = get_results_per_page(request)

    paginator = Paginator(results, results_per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "result_count": paginator.count,
        "results_per_page": results_per_page,
        "search_text": search_text,
        "page": page_obj,
        "title": _("Patron Management"),
        "patron_mode": True,
    }

    return render(request, "staff/user_management.html", context)


@permission_required("users.create_patron_account")
def create_patron(request):
    if request.method == "POST":
        form = PatronForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Don't worry about duplicates. We need one address per person, even if
            # multiple people live at the same place. They won't live there forever.
            newuserlocation = USLocation.objects.create(
                address_1=data["address_1"],
                address_2=data["address_2"],
                city=data["city"],
                state=data["state"],
                zip_code=data["zip_code"],
                host=request.get_host(),
            )
            newuser = User.objects.create_user(
                address=newuserlocation,
                card_number=data["card_number"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                is_minor=data["is_minor"],
                birth_year=data["birth_year"],
                notes=data["notes"],
                default_branch=data["default_branch"],
                is_staff=data["is_staff"],
            )
            messages.success(request, _("User created!"))
            # Todo: send an email to the newly created user welcoming them to the system!
            return HttpResponseRedirect(
                reverse("edit_patron", args=[newuser.card_number])
            )
        else:
            return render(
                request,
                "staff/userform.html",
                {
                    "form": form,
                    "header": _("Register Patron"),
                },
            )

    if request.user.get_work_branch().address:
        # if their account isn't fully set up yet, this can be None
        city = request.user.get_work_branch().address.city
        state = request.user.get_work_branch().address.state
    else:
        city = None
        state = None

    form = PatronForm(
        initial={
            "default_branch_queryset": request.user.get_branches(),
            "default_branch": request.user.get_work_branch(),
            "city": city,
            "state": state,
        }
    )
    return render(
        request,
        "staff/userform.html",
        {
            "form": form,
            "header": _("Register Patron"),
        },
    )


class EditPatronUser(PermissionRequiredMixin, View):
    permission_required = "users.change_patron_account"

    def get(self, request, user_id):
        if request.user.is_superuser:
            user = get_object_or_404(User, card_number=user_id)
        else:
            user = get_object_or_404(User, card_number=user_id, host=request.get_host())

        form = PatronEditForm(
            initial={
                "card_number": user.card_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_minor": user.is_minor,
                "birth_year": user.birth_year,
                "notes": user.notes,
                "default_branch": user.get_default_branch(),
                "default_branch_queryset": user.get_branches(),
                "address_1": user.address.address_1,
                "address_2": user.address.address_2,
                "city": user.address.city,
                "state": user.address.state,
                "zip_code": user.address.zip_code,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
            },
        )
        return render(
            request,
            "staff/userform.html",
            {
                "form": form,
                "header": _("Edit Patron"),
            },
        )

    def post(self, request, user_id):
        if request.user.is_superuser:
            user = get_object_or_404(User, card_number=user_id)
        else:
            # A non-superuser can only edit users belonging to their own host
            user = get_object_or_404(User, card_number=user_id, host=request.host)

        form = PatronEditForm(request.POST)
        if form.is_valid():
            user.update_from_form(form)
            messages.success(request, _("User updated!"))

        # if there are errors, they should automatically propogate to the form
        return HttpResponseRedirect(reverse("edit_patron", args=[user.card_number]))


@permission_required("users.read_patron_account")
def view_patron_account(request, user_id):
    user = get_object_or_404(User, card_number=user_id)
    checkouts = user.checkouts.all()
    holds = Hold.objects.filter(placed_for=user)

    return render(
        request,
        "staff/patron_account_view.html",
        {
            "page_title": _("View Patron"),
            "user": user,
            "checkouts": checkouts,
            "holds": holds,
        },
    )
