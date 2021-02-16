import io
from urllib.parse import quote_plus
import random

import pymarc
import requests
from django.conf import settings
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.aggregates import Count
from django.db.models.expressions import F, Q
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from catalog.forms import LoCSearchForm, LoginForm
from catalog.helpers import build_context
from catalog.marc import import_from_marc
from catalog.models import Record


def index(request: WSGIRequest) -> HttpResponse:
    context = build_context()
    return render(request, "catalog/index.html", context)


def search(request: WSGIRequest) -> HttpResponse:
    context = build_context()
    search_term = request.GET.get("q")
    for item in settings.IGNORED_SEARCH_TERMS:
        search_term = search_term.replace(item, "")

    # TODO: refactor for SearchVector and SearchRank -- requires Postgres
    # https://docs.djangoproject.com/en/dev/ref/contrib/postgres/search/#searchvector
    results = (
        Record.objects.filter(
            Q(title__icontains=search_term) | Q(authors__icontains=search_term)
        )
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

    if search_term:
        context.update(
            {
                "search_term": search_term,
                "results": results,
            }
        )
    return render(request, "catalog/search.html", context)


def add_from_loc(request: WSGIRequest) -> HttpResponse:
    context = build_context()

    if request.method == "POST":
        form = LoCSearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            search_string = quote_plus(data.get("search_term"))
            results = requests.get(
                f"https://www.loc.gov/books/?fo=json&all=true&q={search_string}"
            )
            # lots of results come back, but for testing we're just using the first
            context["result"] = results.json()["results"]

    form = LoCSearchForm()
    context["form"] = form
    return render(request, "catalog/add_from_loc.html", context)


def import_marc_record_from_loc(request):
    loc_id = request.GET.get("loc")
    record = pymarc.parse_xml_to_array(
        io.BytesIO(requests.get("https:" + loc_id + "/marcxml").content)
    )[0]
    import_from_marc(record)

    return render(request, "catalog/add_from_loc.html", build_context())


def place_hold(request, item_id):
    # TODO: build hold system
    return HttpResponse(status=random.choice([200, 403]))


class LoginView(View):
    def get(self, request):
        return render(request, 'generic_form.html', build_context({'form': LoginForm}))
