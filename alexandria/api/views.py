from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from alexandria.api.authentication import CsrfExemptSessionAuthentication
from alexandria.api.serializers import HoldSerializer, ItemSerializer, RecordSerializer
from alexandria.records.models import Hold, Item, ItemType, Record, CheckoutSession
from alexandria.users.models import BranchLocation, User

# holds
SUCCESS = status.HTTP_201_CREATED
HOLD_ALREADY_EXISTS = status.HTTP_409_CONFLICT
YOU_ALREADY_HAVE_THIS_CHECKED_OUT = status.HTTP_406_NOT_ACCEPTABLE
MISSING_ITEM = status.HTTP_412_PRECONDITION_FAILED

# checkout
CHECKOUT_ERROR = status.HTTP_406_NOT_ACCEPTABLE
NO_ACTIVE_SESSION = status.HTTP_410_GONE
EXPIRED_SESSION = status.HTTP_423_LOCKED


def message_response(message: str, status: int) -> Response:
    # Helper function so I don't have to format it every time.
    return Response(data={"message": str}, status=status)


def create_hold(request, item, location, specific_copy=False) -> Response:
    filters = {
        "item": item,
        "host": request.host,
    }

    if patron_id := request.session.get("acting_as_patron"):
        # We're currently impersonating a patron and placing a hold in their name.
        # Reroute the next step so that we set the hold as them and not ourselves.
        target_account = User.objects.get(card_number=patron_id)
    else:
        # We'll land here the grand majority of the time. This is someone setting
        # a hold for themselves.
        target_account = request.user

    # sanity check: can't put something on hold that you already have checked out.
    if item.checked_out_to == target_account:
        return Response(status=YOU_ALREADY_HAVE_THIS_CHECKED_OUT)

    filters.update({"placed_for": target_account})

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
    def renew(self, request, pk=None):
        target = get_object_or_404(Item, pk=pk, host=request.host)

        if (
            request.user != target.checked_out_to
            and not request.user.account_type.is_staff
        ):
            # Staff can hit this, but otherwise if the thing ain't yours then
            # you can't renew it
            return Response(status=status.HTTP_403_FORBIDDEN)

        if request.user.account_type.is_staff or target.can_renew():
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
        location_id: int = request.data["location_id"]
        target = get_object_or_404(Item, id=pk)
        location = get_object_or_404(BranchLocation, id=location_id)
        return create_hold(request, target, location, specific_copy=True)


class HoldViewSet(GenericViewSet):
    queryset = Hold.objects.all()
    serializer_class = HoldSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def destroy(self, request, pk=None, **kwargs) -> Response:
        hold = get_object_or_404(Hold, id=pk)
        if hold.placed_for != request.user:
            # Only staff or the person who placed the hold should be able to remove it.
            if not request.user.account_type.is_staff:
                return Response(status=status.HTTP_403_FORBIDDEN)

        hold.delete()
        return Response(status=status.HTTP_200_OK)


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
            return Response(status=MISSING_ITEM)
        return create_hold(request, item, location)


class CheckoutViewSet(GenericViewSet):
    @action(methods=["post"], detail=False)
    def checkout_item(self, request: Request) -> Response:
        session: CheckoutSession = request.user.get_active_checkout_session()
        if not session:
            return message_response(
                message=_("There is no checkout session currently active."),
                status=NO_ACTIVE_SESSION,
            )

        # By default, a session is valid for 24 hours. Don't leave the browser tab open
        # for more than a day.
        if (
            session.updated_at
            + timezone.timedelta(
                hours=request.context.get("max_checkout_session_hours", 24)
            )
            < timezone.now()
        ):
            session.delete()
            return message_response(
                message=_("The checkout session has expired."), status=EXPIRED_SESSION
            )

        item_id = request.data.get("item_id")
        patron_id = request.data.get("patron_id")

        if not item_id:
            return message_response(
                message=_("Missing item ID... please try again."),
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not patron_id:
            return message_response(
                message=_("Missing patron ID... please try again."),
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = get_object_or_404(Item, id=item_id)
        patron = get_object_or_404(User, card_number=patron_id)

        check, message = patron.can_checkout_item(item)

        if not check:
            return message_response(message=message, status=CHECKOUT_ERROR)

        # We got this far, so we can actually do the checkout thing now.
        session.items.add(item)
        return message_response(message=message, status=SUCCESS)

    @action(methods=["post"], detail=False)
    def get_receipt(self, request: Request) -> Response:
        session: CheckoutSession = request.user.get_active_checkout_session()
        if not session:
            return message_response(
                message=_("There is no checkout session currently active."),
                status=NO_ACTIVE_SESSION,
            )

        # Even if the session is expired, we should be able to get the receipt and
        # finish the session.

        receipt_data = session.get_receipt()
        ...
