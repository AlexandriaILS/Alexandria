from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models.expressions import Q
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, reverse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from alexandria.catalog.helpers import get_results_per_page
from alexandria.records.models import Hold
from alexandria.searchablefields.strings import clean_text
from alexandria.users.forms import PatronEditForm, PatronForm
from alexandria.users.models import AccountType, User, USLocation
from alexandria.utils.type_hints import Request


@csrf_exempt
@permission_required("users.read_patron_account")
def patron_management(request: Request):
    results = request.user.get_viewable_patrons()
    if search_text := request.POST.get("search_text"):
        search_text = clean_text(search_text)
        for word in search_text.split():
            results = results.filter(
                Q(searchable_first_name__icontains=word)
                | Q(searchable_last_name__icontains=word)
                | Q(searchable_chosen_first_name__icontains=word)
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
        "paginator": paginator,
        "title": _("Patron Management"),
        "patron_mode": True,
    }

    return render(request, "staff/user_management.html", context)


@permission_required("users.change_patron_account")
def act_as_user(request, user_id: str):
    # Take the requested user id, add it to the session, and redirect
    # to the catalog so that we can put things on hold for the user

    args = {"card_number": user_id}

    patron = get_object_or_404(User, **args)
    request.session["acting_as_patron"] = patron.card_number
    return HttpResponseRedirect(reverse("homepage"))


@permission_required("users.change_patron_account")
def end_act_as_user(request):
    # remove the target user ID from the session and redirect to the
    # user detail page on the staff side.
    user_id = request.session.get("acting_as_patron")
    try:
        del request.session["acting_as_patron"]
    except KeyError:
        pass

    args = {"card_number": user_id}

    user_exists = bool(User.objects.filter(**args, host=request.host).first())
    if user_exists:
        return HttpResponseRedirect(reverse("view_user", args=[user_id]))
    else:
        return HttpResponseRedirect(reverse("staff_index"))


@permission_required("users.create_patron_account")
def create_patron(request: Request) -> HttpResponse:
    if request.method == "POST":
        form = PatronForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # check to make sure we have a valid account type before creating any data
            account_type = AccountType.objects.filter(
                id=form.data.get("account_type"), host=request.host
            ).first()
            if not account_type:
                raise ValidationError

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
                chosen_first_name=data["chosen_first_name"],
                last_name=data["last_name"],
                email=data["email"],
                is_minor=data["is_minor"],
                birth_year=data["birth_year"],
                notes=data["notes"],
                default_branch=data["default_branch"],
                account_type=account_type,
            )
            # Todo: send an email to the newly created user welcoming them to the system!
            return HttpResponseRedirect(
                reverse("view_user", args=[newuser.card_number])
            )
        else:
            return render(
                request,
                "staff/staff_form.html",
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
            "account_type": None,
            "default_account_type_queryset": request.user.get_account_types().filter(
                is_staff=False
            ),
        }
    )
    return render(
        request,
        "staff/staff_form.html",
        {
            "form": form,
            "header": _("Register Patron"),
        },
    )


class EditPatronUser(PermissionRequiredMixin, View):
    permission_required = "users.change_patron_account"

    def get(self, request, user_id):
        user = get_object_or_404(User, card_number=user_id, host=request.host)

        initial_data = {
            "card_number": user.card_number,
            "first_name": user.first_name,
            "chosen_first_name": user.chosen_first_name,
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
            "is_active": user.is_active,
            "account_type": user.account_type,
        }

        acc_type_qs = user.get_account_types()
        if not request.user.has_perm("users.change_accounttype"):
            # staff members who have access to modify patron accounts but not change
            # staff account types can flip between different patron account types
            acc_type_qs = acc_type_qs.filter(is_staff=False)

        initial_data.update({"default_account_type_queryset": acc_type_qs})

        form = PatronEditForm(initial=initial_data)
        return render(
            request,
            "staff/staff_form.html",
            {
                "form": form,
                "header": _("Edit Patron"),
            },
        )

    def post(self, request, user_id):
        user = get_object_or_404(User, card_number=user_id, host=request.host)

        form = PatronEditForm(request.POST)
        if form.is_valid():
            # because we add account_type conditionally, it won't be here in the form
            if "account_type" in request.POST:
                # do they have the right permission?
                if request.user.has_perm("users.change_accounttype"):
                    # does the account type exist?
                    acc_type = AccountType.objects.filter(
                        id=request.POST.get("account_type")
                    ).first()
                    # is it valid for this library?
                    if acc_type in request.user.get_account_types():
                        # Add it. they'll save in update_from_form
                        user.account_type = acc_type

            user.update_from_form(form)
            messages.success(request, _("User updated!"))

        # if there are errors, they should automatically propagate to the form
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
            "show_legal_name": True,
            "user": user,
            "checkouts": checkouts,
            "holds": holds,
        },
    )
