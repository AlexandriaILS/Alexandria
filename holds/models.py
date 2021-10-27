from django.conf import settings
from django.db import models
from django.utils import timezone

from users.models import AlexandriaUser, BranchLocation


class Hold(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    placed_by = models.ForeignKey(AlexandriaUser, on_delete=models.CASCADE)
    # TODO: Add data cleanup to remove expired holds / migrate to primary location
    destination = models.ForeignKey(BranchLocation, on_delete=models.SET_NULL, null=True)

    item = models.ForeignKey(
        "catalog.Item", null=True, blank=True, on_delete=models.CASCADE
    )
    record = models.ForeignKey(
        "catalog.Record", null=True, blank=True, on_delete=models.CASCADE
    )

    # for when they place a generic hold on a record
    requested_item_type = models.ForeignKey(
        "catalog.ItemType", null=True, blank=True, on_delete=models.CASCADE
    )

    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)


    def __str__(self):
        if self.item:
            return f"{self.item} heading to {self.destination}"
        else:
            return f"{self.record} heading to {self.destination}"
