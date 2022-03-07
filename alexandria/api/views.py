from django.http import HttpResponse
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from alexandria.api.authentication import CsrfExemptSessionAuthentication
from alexandria.api.serializers import ItemSerializer, HoldSerializer, RecordSerializer
from alexandria.records.models import Hold, Item, Record, ItemType
from alexandria.users.models import BranchLocation

SUCCESS = 201
HOLD_ALREADY_EXISTS = 409
YOU_ALREADY_HAVE_THIS_CHECKED_OUT = 406


def create_hold(request, item, location, specific_copy=False) -> Response:
    filters = {
        "placed_for": request.user,
        "item": item,
        "host": request.host,
    }

    # sanity check: can't put something on hold that you already have checked out.
    if item.checked_out_to == request.user:
        return Response(status=YOU_ALREADY_HAVE_THIS_CHECKED_OUT)

    existing = Hold.objects.filter(**filters).first()
    if existing:
        return Response(status=HOLD_ALREADY_EXISTS)

    filters.update({"specific_copy": specific_copy, "destination": location})
    new_hold = Hold.objects.create(**filters)

    return Response(
        {
            "name": item.type.name,
            "hold_number": new_hold.get_hold_queue_number(),
        },
        status=SUCCESS,
    )


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    @action(methods=["get"], detail=True)
    def renew(self, request, item_id=None):
        target = get_object_or_404(Item, id=item_id, host=request.host)

        if request.user != target.checked_out_to and not request.user.is_staff:
            # Staff can hit this, but otherwise if the thing ain't yours then
            # you can't renew it
            return Response(status=status.HTTP_403_FORBIDDEN)

        if request.user.is_staff or target.can_renew():
            target.renewal_count += 1
            target.due_date = target.calculate_renewal_due_date()
            target.save()
            return Response(
                status=status.HTTP_200_OK,
                data={"new_due_date": target.due_date.strftime("%b. %d, %Y")},
            )

        return Response(status=status.HTTP_403_FORBIDDEN)

    @action(methods=["post"], detail=True)
    def place_hold(self, request, pk: int = None):
        # TODO: We don't actually need obj_type here because it's only used for Records,
        #  so it should be adjusted in holdbuttons.js, the route, and here.
        location_id: int = request.data["location_id"]
        if not request.user.is_authenticated:
            return HttpResponse(status=401)
        target = get_object_or_404(Item, id=pk)
        location = get_object_or_404(BranchLocation, id=location_id)
        return create_hold(request, target, location, specific_copy=True)


class HoldViewSet(ModelViewSet):
    queryset = Hold.objects.all()
    serializer_class = HoldSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def destroy(self, request, pk=None) -> Response:
        hold = get_object_or_404(Hold, id=pk)
        if not hold.placed_for == request.user or not request.user.is_staff:
            # Only staff or the person who placed the hold should be able to remove it.
            return Response(status=403)

        hold.delete()
        return Response(status=200)


class RecordViewSet(ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [CsrfExemptSessionAuthentication]

    @action(methods=["post"], detail=True, permission_classes=[IsAuthenticated])
    def place_hold(self, request: Request, pk: int) -> Response:
        # An incoming hold on a record should immediately be converted into an item.
        # After that, the item can be placed on hold.
        # We always want to circulate the _most recently checked out copy_. This is
        # because the oldest circulating copy may be lost, and that's just a part
        # of life.
        item_type_id: int = request.data["item_type_id"]
        location_id: int = request.data["location_id"]

        item_type = get_object_or_404(ItemType, id=item_type_id)
        target = get_object_or_404(Record, id=pk)
        location = get_object_or_404(BranchLocation, id=location_id)

        # First, check to see if there's a copy in the location that's the hold will
        # be picked up at.
        item = (
            target.item_set.filter(
                home_location=location,
                type=item_type,
                host=request.host,
                is_active=True,
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
                    is_active=True,
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
            return Response(status=412)  # 410 gone
        return create_hold(request, item, location)
