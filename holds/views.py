import random
from typing import Union

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404

from catalog.models import ItemType, Record, Item
from holds.models import Hold
from users.models import BranchLocation
from utils.db import filter_db

SUCCESS = 200
HOLD_ALREADY_EXISTS = 409


def get_hold_queue_number(new_hold: Hold) -> int:
    # TODO: this is super simplistic and is only accurate if called right when
    #  the hold is created.
    return Hold.objects.filter(item=new_hold.item, record=new_hold.record, requested_item_type=new_hold.requested_item_type).order_by(
        "-date_created"
    ).count()


def create_hold(request, obj, obj_type, location) -> Union[HttpResponse, JsonResponse]:
    # TODO: figure out location issue
    #  What if there's a modal when someone clicks on the quick hold button that asks
    #  where they want it to go and defaults to the user's chosen location?
    filters = {
        'placed_by': request.user,
        'requested_item_type': obj_type,
        'destination': location
    }
    obj_db_reference = {}
    if isinstance(obj, Record):
        obj_db_reference['record'] = obj
    else:
        # it's an Item
        obj_db_reference['item'] = obj

    filters.update(obj_db_reference)
    existing = filter_db(request, Hold, **filters).first()
    if existing:
        return HttpResponse(status=HOLD_ALREADY_EXISTS)

    new_hold = Hold.objects.create(**filters)

    return JsonResponse(
        {
            "name": obj.type.name,
            "hold_number": get_hold_queue_number(new_hold),
        },
        status=SUCCESS,
    )


def place_hold_on_record(
        request: WSGIRequest, item_id: int, item_type_id: int, location_id: int
) -> Union[JsonResponse, HttpResponse]:
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    itemtype = get_object_or_404(ItemType, id=item_type_id)
    target = get_object_or_404(Record, id=item_id)
    location = get_object_or_404(BranchLocation, id=location_id)
    return create_hold(request, target, itemtype, location)


def place_hold_on_item(
        request: WSGIRequest, item_id: int, item_type_id: int, location_id: int
) -> Union[JsonResponse, HttpResponse]:
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    itemtype = get_object_or_404(ItemType, id=item_type_id)
    target = get_object_or_404(Item, id=item_id)
    location = get_object_or_404(BranchLocation, id=location_id)
    return create_hold(request, target, itemtype, location)
