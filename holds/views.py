import random
from typing import Union

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404

from catalog.models import ItemType, Record, Item
from holds.models import Hold

SUCCESS = 200
HOLD_ALREADY_EXISTS = 409


def get_hold_queue_number(request: WSGIRequest, new_hold: Hold) -> int:
    all_holds_for_obj = Hold.objects.filter(target=new_hold.target).order_by("-date_created")
    ...


def create_hold(request, obj, obj_type) -> Union[HttpResponse, JsonResponse]:
    if Hold.objects.filter(placed_by=request.user, target=obj, requested_item_type=obj_type).first():
        return HttpResponse(status=HOLD_ALREADY_EXISTS)

    if isinstance(obj, Record):
        new_hold = Hold.objects.create(placed_by=request.user, target=obj, requested_item_type=obj_type)
    else:
        # it's an Item
        new_hold = Hold.objects.create(placed_by=request.user, target=obj)

    return JsonResponse(
        {"name": obj.type.name, "hold_number": get_hold_queue_number(request, new_hold)},
        status=SUCCESS,
    )


def place_hold_on_record(request: WSGIRequest, item_id: int, item_type_id: int) -> Union[JsonResponse, HttpResponse]:
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    itemtype = get_object_or_404(ItemType, id=item_type_id)
    target = get_object_or_404(Record, id=item_id)
    return create_hold(request, target, itemtype)


def place_hold_on_item(request: WSGIRequest, item_id: int, item_type_id: int) -> Union[JsonResponse, HttpResponse]:
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    itemtype = get_object_or_404(ItemType, id=item_type_id)
    target = get_object_or_404(Item, id=item_id)
    return create_hold(request, target, itemtype)
