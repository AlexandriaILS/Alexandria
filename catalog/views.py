import io
from urllib.parse import quote_plus
import random

import pymarc
import requests
from django.conf import settings
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.aggregates import Count
from django.db.models.expressions import F, Q
from django.db.models.functions import Lower
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, reverse
from django.views.generic import View
from django.core.paginator import Paginator

from catalog.forms import CombinedRecordItemEditForm, LoCSearchForm, LoginForm
from catalog.helpers import build_context, get_results_per_page
from catalog.marc import import_from_marc
from catalog.models import Record, Item, ItemType


def index(request: WSGIRequest) -> HttpResponse:
    context = build_context()
    return render(request, "catalog/index.html", context)


def search(request: WSGIRequest) -> HttpResponse:
    context = build_context()
    search_term = request.GET.get("q")
    if not search_term:
        return render(request, "catalog/search.html", context)

    search_term = " ".join([i for i in search_term.split() if i not in settings.IGNORED_SEARCH_TERMS])

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
    results_per_page = get_results_per_page(request)

    paginator = Paginator(results, results_per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context.update(
        {"result_count": paginator.count, "results_per_page": results_per_page}
    )

    if search_term:
        context.update(
            {"search_term": search_term, "results": results, "page": page_obj}
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
    item = import_from_marc(record)

    return HttpResponseRedirect(reverse("item_edit", args=(item.id,)))


def place_hold(request, item_id, item_type_id):
    SUCCESS = 200
    HOLD_ALREADY_EXISTS = 409
    # TODO: build hold system
    itemtype = ItemType.objects.filter(id=item_type_id).first()
    if itemtype:
        return JsonResponse(
            {"name": itemtype.name},
            status=random.choice([SUCCESS, HOLD_ALREADY_EXISTS, 403]),
        )
    else:
        return HttpResponse(404)


class LoginView(View):
    def get(self, request):
        return render(request, "generic_form.html", build_context({"form": LoginForm}))

    def post(self, request):
        ...


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, "catalog/item_detail.html", build_context({"item": item}))


class ItemEdit(View):
    def get(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        data = {
            "title": item.record.title,
            "authors": item.record.authors,
            "subtitle": item.record.subtitle,
            "uniform_title": item.record.uniform_title,
            "notes": item.record.notes,
            "series": item.record.series,
            "record_type": item.record.type,
            "record_bibliographic_level": item.record.bibliographic_level,
            "summary": item.record.summary,
            "barcode": item.barcode,
            "price": item.price,
            "publisher": item.publisher,
            "is_active": item.is_active,
            "pubyear": item.pubyear,
            "item_bibliographic_level": item.bibliographic_level,
            "item_type": item.type,
        }
        form = CombinedRecordItemEditForm(initial=data)
        return render(request, "generic_form.html", {"form": form})

    def post(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        record = item.record
        form = CombinedRecordItemEditForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            record.title = data["title"]
            record.authors = data["authors"]
            record.subtitle = data["subtitle"]
            record.uniform_title = data["uniform_title"]
            record.notes = data["notes"]
            record.series = data["series"]
            record.type = data["record_type"]
            record.bibliographic_level = data["record_bibliographic_level"]
            record.summary = data["summary"]

            item.barcode = data["barcode"]
            item.price = data["price"]
            item.publisher = data["publisher"]
            item.is_active = data["is_active"]
            item.pubyear = data["pubyear"]
            item.bibliographic_level = data["item_bibliographic_level"]
            item.type = data["item_type"]

            record.save()
            item.save()
            return HttpResponseRedirect(reverse("item_detail", args=(item.id,)))
