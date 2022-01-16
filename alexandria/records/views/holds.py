from typing import Union

from django.http import HttpResponse, JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404

from alexandria.records.models import ItemType, Record, Item
from alexandria.records.models import Hold
from alexandria.users.models import BranchLocation
from alexandria.utils.db import filter_db

SUCCESS = 200
HOLD_ALREADY_EXISTS = 409
YOU_ALREADY_HAVE_THIS_CHECKED_OUT = 406


def create_hold(
    request, item, location, specific_copy=False
) -> Union[HttpResponse, JsonResponse]:
    filters = {
        "placed_by": request.user,
        "destination": location,
        "item": item,
    }

    # sanity check: can't put something on hold that you already have checked out.
    if item.checked_out_to == request.user:
        return HttpResponse(status=YOU_ALREADY_HAVE_THIS_CHECKED_OUT)

    existing = filter_db(request, Hold, **filters).first()
    if existing:
        return HttpResponse(status=HOLD_ALREADY_EXISTS)

    filters.update({"specific_copy": specific_copy})
    new_hold = Hold.objects.create(**filters)

    return JsonResponse(
        {
            "name": item.type.name,
            "hold_number": new_hold.get_hold_queue_number(),
        },
        status=SUCCESS,
    )


def delete_hold(request: WSGIRequest, hold_id: int) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    hold = get_object_or_404(Hold, id=hold_id)
    if not hold.placed_by == request.user or not request.user.is_staff:
        # Only staff or the person who placed the hold should be able to remove it.
        return HttpResponse(status=403)

    hold.delete()
    return HttpResponse(status=200)


def place_hold_on_record(
    request: WSGIRequest, item_id: int, item_type_id: int, location_id: int
) -> Union[JsonResponse, HttpResponse]:
    # An incoming hold on a record should immediately be converted into an item.
    # After that, the item can be placed on hold.
    # We always want to circulate the _most recently checked out copy_. This is
    # because the oldest circulating copy may be lost, and that's just a part
    # of life.
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    item_type = get_object_or_404(ItemType, id=item_type_id)
    target = get_object_or_404(Record, id=item_id)
    location = get_object_or_404(BranchLocation, id=location_id)

    # First, check to see if there's a copy in the location that's the hold will
    # be picked up at.
    item = (
        target.item_set.filter(
            home_location=location, type=item_type, host=request.host
        )
        .order_by("-last_checked_out")
        .first()
    )
    if not item:
        # If that doesn't work, get the most recently used copy from the system.
        item = (
            target.item_set.filter(
                home_location__id__in=BranchLocation.objects.exclude(
                    id=location.id, host=request.host
                ),
                type=item_type,
                host=request.host,
            )
            .order_by("-last_checked_out")
            .first()
        )
    if not item:
        # We shouldn't get here. Ever. If we're placing a hold, there should always
        # be a valid target for the hold. But just in case there isn't... we should
        # handle it.
        # TODO: Add handling for this in holdbuttons.js
        return HttpResponse(status=412)  # 410 gone
    return create_hold(request, item, location)


def place_hold_on_item(
    request: WSGIRequest, item_id: int, item_type_id: int, location_id: int
) -> Union[JsonResponse, HttpResponse]:
    # TODO: We don't actually need obj_type here because it's only used for Records,
    #  so it should be adjusted in holdbuttons.js, the route, and here.
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    target = get_object_or_404(Item, id=item_id)
    location = get_object_or_404(BranchLocation, id=location_id)
    return create_hold(request, target, location, specific_copy=True)


def renew_hold_on_item(request: WSGIRequest, item_id: int):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    target = get_object_or_404(Item, id=item_id, host=request.host)

    if target.can_renew():
        target.renewal_count += 1
        target.due_date = target.calculate_renewal_due_date()
        target.save()
        return JsonResponse(
            status=200, data={"new_due_date": target.due_date.strftime("%b. %d, %Y")}
        )
    return HttpResponse(status=403)
