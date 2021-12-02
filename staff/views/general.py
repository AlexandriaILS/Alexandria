from urllib.parse import quote_plus

from django.core.paginator import Paginator
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.db.models.aggregates import Count
from django.db.models.expressions import F, Q
from django.db.models.functions import Lower
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import View
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from catalog.helpers import get_results_per_page
from catalog.models import Item, Record
from staff.forms import StaffSettingsForm
from users.models import AlexandriaUser
from utils.db import filter_db
from utils.strings import clean_text
from utils.permissions import permission_to_perm, permission_or_none


# Create your views here.
# TODO: create checkout views
# TODO: move material management views
# TODO: add reports functionality
# TODO: add user management


@csrf_exempt
def index(request):
    if request.method == "POST":
        additions = []
        search_text = request.POST.get("search_text")
        search_type = request.POST.get("search_type")
        if search_text:
            additions += ["q=" + quote_plus(search_text) if search_text else ""]
            additions += ["type=" + quote_plus(search_type) if search_type else ""]
            additions = "?" + "&".join(additions)
        else:
            # form was submitted, but no content was detected.
            return HttpResponseRedirect(reverse("staff_index"))
        return HttpResponseRedirect(reverse("staff_search") + additions)
    return render(request, "staff/index.html", {"page_title": "Quick Search"})


@permission_or_none('catalog.view_item')
def record_search(request, term, title=False, author=False):
    filters = Q()
    if title:
        filters = filters | Q(searchable_title__icontains=term)
    if author:
        filters = filters | Q(searchable_authors__icontains=term)
    return (
        Record.objects.filter(filters, host=request.host)
            .exclude(
            id__in=(
                Record.objects.annotate(total_count=Count("item", distinct=True))
                    .filter(item__is_active=False)
                    .annotate(is_active=Count("item", distinct=True))
                    .filter(Q(is_active=F("total_count")))
            )
        )
            .exclude(id__in=Record.objects.filter(item__isnull=True))
            .order_by(Lower("title"))
    )


@permission_or_none('catalog.view_item')
def item_search(request, term):
    return Item.objects.filter(barcode=term, is_active=True, host=request.host)


@permission_or_none('users.read_patron_account')
def patron_search(request, term):
    return AlexandriaUser.objects.filter(
        Q(searchable_first_name__icontains=term)
        | Q(searchable_last_name__icontains=term)
        | Q(card_number=term),
        is_active=True,
        host=request.host
    )


def staff_search(request):
    # TODO: Add colors to checked in or checked out in staff view

    search_term = request.GET.get("q")
    search_type = request.GET.get("type")
    if not search_term:
        return render(request, "staff/search.html")

    search_term = " ".join(
        [
            i
            for i in search_term.split()
            if i not in request.context["ignored_search_terms"]
        ]
    )
    data = {}
    if search_type == "title":
        data["record_results"] = record_search(request, search_term, title=True)
    elif search_type == "author":
        data["record_results"] = record_search(request, search_term, author=True)
    elif search_type == "barcode":
        data["item_results"] = item_search(request, search_term)
        data["patron_results"] = patron_search(request, search_term)
    elif search_type == "patron":
        data["patron_results"] = patron_search(request, search_term)
    else:
        # everything
        data["record_results"] = record_search(request, search_term, author=True, title=True)
        data["item_results"] = item_search(request, search_term)
        data["patron_results"] = patron_search(request, search_term)

    return render(request, "staff/search.html", {"results": data})


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
    }

    return render(request, "staff/user_management.html", context)


@csrf_exempt
@permission_required("users.read_staff_account")
def staff_management(request):
    results = request.user.get_modifiable_staff()
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
    }

    return render(request, "staff/user_management.html", context)


class EditStaffUser(PermissionRequiredMixin, View):
    permission_required = "users.change_staff_account"

    def get(self, request, user_id):
        user = get_object_or_404(AlexandriaUser, card_number=user_id)
        form = StaffSettingsForm(
            request=request,
            initial={
                "card_number": user.card_number,
                "title": user.title,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_minor": user.is_minor,
                "birth_year": user.birth_year,
                "notes": user.notes,
                "default_branch": user.default_branch,
                "default_branch_queryset": user.get_branches(),
                "address_1": user.address.address_1,
                "address_2": user.address.address_2,
                "city": user.address.city,
                "state": user.address.state,
                "zip_code": user.address.zip_code,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
                "permissions_initial": user.get_all_permissions(),
            },
        )
        perm_groups = request.user.get_viewable_permissions_groups()
        permissions_defaults = {
            group.name: [i[0] for i in group.permissions.values_list("id")]
            for group in perm_groups
        }
        return render(
            request,
            "staff/permissions.html",
            {
                "form": form,
                "multiwidgetdefaults": permissions_defaults,
                "header": _("Edit Staff User"),
            },
        )

    def post(self, request, user_id):
        user = get_object_or_404(AlexandriaUser, card_number=user_id)
        form = StaffSettingsForm(request.POST)

        if form.is_valid():
            # We'll only get back a list of the objects that are toggled on, so we can
            # act directly on those. First we filter them out because they won't show
            # up in the cleaned_data, then we validate that they're actually perms and
            # that they can be awarded in the first place. Then we parse the rest of
            # the data.
            permissions = [
                i for i in form.data.keys() if i not in form.cleaned_data.keys()
            ]
            permission_objects = Permission.objects.filter(codename__in=permissions)
            # Only process the permissions that we have ourselves. There's no
            # reasonable way this should be an issue, but... sometimes you never know.
            valid_perms = []

            for permission in permission_objects:
                if request.user.has_perm(permission_to_perm(permission)):
                    valid_perms.append(permission)

            user.groups.clear()
            user.user_permissions.clear()
            user.user_permissions.set(valid_perms)

            for key in form.cleaned_data.keys():
                if key == "permissions":
                    continue
                if hasattr(user, key):
                    setattr(user, key, form.cleaned_data[key])

            # the rest of these are related to the address FK
            unhandled_keys = [i for i in form.cleaned_data.keys() if i not in dir(user)]
            for key in unhandled_keys:
                if hasattr(user.address, key):
                    setattr(user.address, key, form.cleaned_data[key])

            user.address.save()
            user.save()

            messages.success(request, _("Updated account!"))
        else:
            messages.error(request, _("Something went wrong. Please try again."))
        # no matter what happens, return to the same page.
        return redirect("edit_staff_user", user_id=user_id)
