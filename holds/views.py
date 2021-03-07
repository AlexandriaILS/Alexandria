import random

from django.http import HttpResponse, JsonResponse

from catalog.models import ItemType


def place_hold_on_record(request, item_id, item_type_id):
    SUCCESS = 200
    HOLD_ALREADY_EXISTS = 409
    # TODO: build hold system
    itemtype = ItemType.objects.filter(id=item_type_id).first()
    if itemtype:
        return JsonResponse(
            {"name": itemtype.name},
            status=random.choice([SUCCESS, SUCCESS, SUCCESS, HOLD_ALREADY_EXISTS, 403]),
        )
    else:
        return HttpResponse(404)


def place_hold_on_item(request, item_id, item_type_id):
    SUCCESS = 200
    HOLD_ALREADY_EXISTS = 409
    # TODO: build hold system
    itemtype = ItemType.objects.filter(id=item_type_id).first()
    if itemtype:
        return JsonResponse(
            {"name": itemtype.name},
            status=random.choice([SUCCESS, SUCCESS, SUCCESS, HOLD_ALREADY_EXISTS, 403]),
        )
    else:
        return HttpResponse(404)
