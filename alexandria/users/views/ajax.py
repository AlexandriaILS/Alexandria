from django.db.models.aggregates import Count
from django.db.models.expressions import F, Q
from django.db.models.functions import Lower

from alexandria.records.models import Item, Record
from alexandria.users.models import User
from alexandria.utils.permissions import permission_or_none


@permission_or_none("catalog.view_item")
def record_search(request, term, title=False, author=False):
    filters = Q()
    if title:
        filters = filters | Q(searchable_title__icontains=term)
    if author:
        filters = filters | Q(searchable_authors__icontains=term)
    return (
        Record.objects.filter(filters, host=request.host)
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


@permission_or_none("catalog.view_item")
def item_search(request, term):
    return Item.objects.filter(barcode=term, is_active=True, host=request.host)


@permission_or_none("users.read_patron_account")
def patron_search(request, term):
    return User.objects.filter(
        Q(searchable_first_name__icontains=term)
        | Q(searchable_last_name__icontains=term)
        | Q(card_number=term),
        is_active=True,
        host=request.host,
    ).order_by("last_name", "-birth_year")
