import io
from urllib.parse import quote_plus

import pymarc
import requests
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse
from django.views.generic import View

from alexandria.records.forms import CombinedRecordItemEditForm, LoCSearchForm
from alexandria.records.marc import import_from_marc
from alexandria.records.models import Item
from alexandria.utils.type_hints import Request


def add_from_loc(request: Request) -> HttpResponse:
    context = dict()

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


def import_marc_record_from_loc(request: Request) -> HttpResponseRedirect:
    loc_id = request.GET.get("loc")
    record = pymarc.parse_xml_to_array(
        io.BytesIO(requests.get("https:" + loc_id + "/marcxml").content)
    )[0]
    item = import_from_marc(record)

    return HttpResponseRedirect(reverse("item_edit", args=(item.id,)))


class ItemEdit(PermissionRequiredMixin, View):
    permission_required = "change_item"

    def get(self, request: Request, item_id: int) -> HttpResponse:
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

    def post(self, request: Request, item_id: int) -> HttpResponse:
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
        # todo: what happens if it falls through?
