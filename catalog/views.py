from urllib.parse import quote_plus
import io

from django.shortcuts import render
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.conf import settings
import requests
import pymarc

from catalog.helpers import build_context
from catalog.forms import LoCSearchForm
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
    results = Record.objects.filter(
        Q(title__icontains=search_term) | Q(authors__icontains=search_term)
    )
    if search_term:
        # TODO: refactor for SearchVector and SearchRank -- requires Postgres
        # https://docs.djangoproject.com/en/dev/ref/contrib/postgres/search/#searchvector
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
            result = results.json()["results"][0]
            record = pymarc.parse_xml_to_array(
                io.BytesIO(requests.get("https:" + result["url"] + "/marcxml").content)
            )[0]
            if data["store"]:
                new_record = import_from_marc(record)
                context["result"] = new_record
            else:
                context["result"] = record.as_dict()

    form = LoCSearchForm()
    context["form"] = form
    return render(request, "catalog/add_from_loc.html", context)
