from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from users.models import AlexandriaUser, BranchLocation


class Hold(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    placed_by = models.ForeignKey(AlexandriaUser, on_delete=models.CASCADE)
    # TODO: Add data cleanup to remove expired holds / migrate to primary location
    destination = models.ForeignKey(
        BranchLocation, on_delete=models.SET_NULL, null=True
    )

    item = models.ForeignKey(
        "catalog.Item", null=True, blank=True, on_delete=models.CASCADE
    )

    # used to see whether we can recalculate a hold in the event that a hold
    # is placed on an item but someone tries to check out the item
    # before it can be pulled
    specific_copy = models.BooleanField(default=False)
    # todo: make this flag only available for managers
    force_next_available = models.BooleanField(
        default=False,
        help_text=(
            "Very rarely, certain holds need to be completed ahead of others. Setting"
            " this makes this hold be processed next, no matter where it is in the queue."
            " If there are multiple holds with this flag, then they will be processed in"
            " order of oldest first."
        )
    )

    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)

    def __str__(self):
        return f"{self.item} heading to {self.destination}"

    def get_hold_queue_number(self):
        open_holds = (
            Hold.objects.filter(
                item=self.item,
            ).order_by("-date_created")
        )
        return (*open_holds,).index(self)

    def is_ready_for_pickup(self):
        return self.item.checked_out_to == BranchLocation.objects.get(name="ready_for_pickup")

    def get_status_for_patron(self):
        if self.is_ready_for_pickup():
            return _("Ready for pickup!")
        else:
            return _("In Progress")

    def get_status_color_class(self):
        if self.is_ready_for_pickup():
            return "success text-light"
        else:
            return "secondary text-light"

    def get_status_for_staff(self):
        ...
