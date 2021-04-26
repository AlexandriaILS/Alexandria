from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType as DjangoContentType
from django.db import models
from django.utils import timezone

from users.models import AlexandriaUser, BranchLocation


class Hold(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    placed_by = models.ForeignKey(AlexandriaUser, on_delete=models.CASCADE)
    # TODO: setting CASCADE here will kill all active hold requests if a location is
    #  deleted -- is that really what we want? Is there a better way to handle this?
    destination = models.ForeignKey(BranchLocation, on_delete=models.CASCADE)

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

    def __str__(self):
        if self.item:
            return f"{self.item} heading to {self.destination}"
        else:
            return f"{self.record} heading to {self.destination}"
