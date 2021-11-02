from django.conf import settings
from django.db import models
from django.utils import timezone

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

    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)

    def __str__(self):
        return f"{self.item} heading to {self.destination}"
