from urllib.parse import quote_plus

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db.models.aggregates import Count
from django.db.models.expressions import F, Q
from django.db.models.functions import Lower
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse
from django.views.decorators.csrf import csrf_exempt

from alexandria.catalog.helpers import get_results_per_page
from alexandria.records.models import Record
from alexandria.utils.db import filter_db


@csrf_exempt
def index(request: WSGIRequest) -> HttpResponse:
    if request.method == "POST":
        search_text = request.POST.get("search_text")
        return HttpResponseRedirect(
            reverse("search") + ("?q=" + quote_plus(search_text)) if search_text else ""
        )
    return render(request, "catalog/index.html")


def search(request: WSGIRequest) -> HttpResponse:
    context = dict()
    search_term = request.GET.get("q")
    if not search_term:
        return render(request, "catalog/search.html", context)

    search_term = " ".join(
        [
            i
            for i in search_term.split()
            if i not in request.context["ignored_search_terms"]
        ]
    )

    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
        # TODO: refactor for SearchVector and SearchRank -- requires Postgres
        # https://docs.djangoproject.com/en/dev/ref/contrib/postgres/search/#searchvector
        results = ...
    else:
        results = (
            filter_db(
                request,
                Record,
                Q(searchable_title__icontains=search_term)
                | Q(searchable_authors__icontains=search_term)
                | Q(searchable_subtitle__icontains=search_term)
                | Q(searchable_uniform_title__icontains=search_term)
                | Q(item__barcode=search_term)
                | Q(item__call_number=search_term),
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
                .distinct()
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


def item_detail(request, item_id):
    record = get_object_or_404(Record, id=item_id, host=request.host)
    return render(
        request, "catalog/item_detail.html", {"record": record}
    )
