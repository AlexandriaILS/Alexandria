from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.core.paginator import Paginator
from django.db.models.expressions import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from alexandria.catalog.helpers import get_results_per_page
from alexandria.searchablefields.strings import clean_text
from alexandria.users.forms import StaffSettingsForm
from alexandria.users.models import User
from alexandria.utils.permissions import permission_to_perm


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
        "title": _("Staff Management"),
    }

    return render(request, "staff/user_management.html", context)


class EditStaffUser(PermissionRequiredMixin, View):
    permission_required = "users.change_staff_account"

    def get(self, request, user_id):
        if request.user.is_superuser:
            user = get_object_or_404(User, card_number=user_id)
        else:
            if user_id == request.user.card_number:
                messages.error(request, _("Sorry, you can't edit your own account."))
                raise Http404

            # A non-superuser can only edit users belonging to their own host
            user = get_object_or_404(User, card_number=user_id, host=request.host)

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
                "default_branch": user.get_default_branch(),
                "default_branch_queryset": user.get_branches(),
                "work_branch": user.get_work_branch(),
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
            "staff/userform.html",
            {
                "form": form,
                "multiwidgetdefaults": permissions_defaults,
                "header": _("Edit Staff User"),
            },
        )

    def post(self, request, user_id):
        # this shouldn't matter but if they send a bogus request against this
        # endpoint, this will protect us
        if request.user.is_superuser:
            user = get_object_or_404(User, card_number=user_id)
        else:
            if user_id == request.user.card_number:
                messages.error(request, _("Sorry, you can't edit your own account."))
                raise Http404

            # A non-superuser can only edit users belonging to their own host
            user = get_object_or_404(User, card_number=user_id, host=request.host)

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
            user.save()

            user.update_from_form(form)

            messages.success(request, _("Updated account!"))
        else:
            messages.error(request, _("Something went wrong. Please try again."))
        # no matter what happens, return to the same page.
        return redirect("edit_staff_user", user_id=user_id)
