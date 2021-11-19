from urllib.parse import quote_plus

from django.db.models.aggregates import Count
from django.db.models.expressions import F, Q
from django.db.models.functions import Lower
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.decorators.csrf import csrf_exempt

from catalog.models import Item, Record
from users.models import AlexandriaUser
from utils.db import filter_db


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


def staff_search(request):
    # TODO: Add colors to checked in or checked out in staff view

    def record_search(term, title=False, author=False):
        filters = Q()
        if title:
            filters = filters | Q(title__icontains=term)
        if author:
            filters = filters | Q(authors__icontains=term)
        return (
            filter_db(request, Record, filters)
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

    def item_search(term):
        return filter_db(request, Item, barcode=term, is_active=True)

    def patron_search(term):
        return filter_db(
            request,
            AlexandriaUser,
            Q(first_name__icontains=term)
            | Q(last_name__icontains=term)
            | Q(card_number=term),
            is_active=True,
        )

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
        data["records"] = record_search(search_term, title=True)
    elif search_type == "author":
        data["records"] = record_search(search_term, author=True)
    elif search_type == "barcode":
        data["items"] = item_search(search_term)
        data["patrons"] = patron_search(search_term)
    elif search_type == "patron":
        data["patrons"] = patron_search(search_term)
    else:
        # everything
        data["records"] = record_search(search_term, author=True, title=True)
        data["items"] = item_search(search_term)
        data["patrons"] = patron_search(search_term)

    return render(request, "staff/search.html", {"results": data})


def user_management(request):
    return render(request, "staff/user_management.html")


class UserEditView():
    ...
