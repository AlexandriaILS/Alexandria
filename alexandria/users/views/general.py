from urllib.parse import quote_plus

from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.decorators.csrf import csrf_exempt

from alexandria.searchablefields.strings import clean_text
from alexandria.users.views.ajax import item_search, patron_search, record_search

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

    search_term = request.GET.get("q")
    search_type = request.GET.get("type")
    if not search_term:
        return render(request, "staff/search.html")

    search_term = " ".join(
        [
            i
            for i in search_term.split()
            if i not in request.settings.ignored_search_terms.split(",")
        ]
    )
    backed_up_search_term = search_term
    search_term = clean_text(search_term)  # convert to searchable format
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
        data["record_results"] = record_search(
            request, search_term, author=True, title=True
        )
        data["item_results"] = item_search(request, search_term)
        data["patron_results"] = patron_search(request, search_term)

    return render(
        request,
        "staff/index.html",
        {
            "results": data,
            "page_title": "Quick Search",
            "search_term": backed_up_search_term,
        },
    )
