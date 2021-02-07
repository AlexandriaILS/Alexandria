from urllib.parse import quote_plus
import io

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import requests
import pymarc

from catalog.helpers import build_context
from catalog.forms import LoCSearchForm
from catalog.marc import import_from_marc


def index(request: HttpRequest) -> HttpResponse:
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
    return render(request, "catalog/index.html", context)
