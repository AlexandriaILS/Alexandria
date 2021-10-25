import io
from urllib.parse import quote_plus

import pymarc
import requests
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db.models.aggregates import Count
from django.db.models.expressions import F, Q
from django.db.models.functions import Lower
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from catalog.forms import CombinedRecordItemEditForm, LoCSearchForm
from catalog.helpers import get_results_per_page
from catalog.marc import import_from_marc
from catalog.models import Record, Item
from users.mixins import LibraryStaffRequiredMixin
from utils import build_context
from utils.db import filter


@csrf_exempt
def index(request: WSGIRequest) -> HttpResponse:
    if request.method == "POST":
        search_text = request.POST.get("search_text")
        return HttpResponseRedirect(
            reverse("search") + ("?q=" + quote_plus(search_text)) if search_text else ""
        )
    context = build_context()
    return render(request, "catalog/index.html", context)


def search(request: WSGIRequest) -> HttpResponse:
    context = build_context()
    search_term = request.GET.get("q")
    if not search_term:
        return render(request, "catalog/search.html", context)

    search_term = " ".join(
        [i for i in search_term.split() if i not in request.context['ignored_search_terms']]
    )

    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
        # TODO: refactor for SearchVector and SearchRank -- requires Postgres
        # https://docs.djangoproject.com/en/dev/ref/contrib/postgres/search/#searchvector
        results = ...
    else:
        results = (
            filter(request, Record, Q(title__icontains=search_term) | Q(authors__icontains=search_term))
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
            try:
                results = requests.get(
                    f"https://www.loc.gov/books/"
                    f"?fo=json&all=true&fa=partof:catalog&q={search_string}"
                )
                # lots of results come back, but for testing we're just using the first
                context["result"] = results.json()["results"]
            except Exception:
                context["error"] = (
                    "Something went wrong and the response isn't usable."
                    " Please try again or try a different import method."
                )

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


def item_detail(request, item_id):
    item = get_object_or_404(Record, id=item_id, host=request.host)
    return render(request, "catalog/item_detail.html", build_context({"item": item}))


class ItemEdit(LibraryStaffRequiredMixin, View):
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
