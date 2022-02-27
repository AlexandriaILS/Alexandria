from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from alexandria.api.serializers import ItemSerializer, HoldSerializer
from alexandria.records.models import Hold, Item, Record


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    @action(methods=["get"], detail=True)
    def renew(self, request, pk=None):
        target = get_object_or_404(Item, id=pk, host=request.host)

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


class HoldViewSet(ModelViewSet):
    queryset = Hold.objects.all()
    serializer_class = HoldSerializer
    permission_classes = [IsAdminUser]

    @action(methods=["get"], detail=True, permission_classes=[IsAuthenticated])
    def renew_hold(self, request, obj):
        ...
