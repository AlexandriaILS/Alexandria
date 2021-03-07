from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType as DjangoContentType
from django.db import models
from django.utils import timezone

from catalog.models import ItemType
from users.models import AlexandriaUser, BranchLocation


class Hold(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    placed_by = models.ForeignKey(AlexandriaUser, on_delete=models.CASCADE)
    # TODO: setting CASCADE here will kill all active hold requests if a location is
    #  deleted -- is that really what we want? Is there a better way to handle this?
    destination = models.ForeignKey(BranchLocation, on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        DjangoContentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        limit_choices_to={
            "model__in": (
                "item",
                "record",
            )
        },
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey("content_type", "object_id")
    # for when they place a generic hold on a record
    requested_item_type = models.ForeignKey(ItemType, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.target} heading to {self.destination}"
