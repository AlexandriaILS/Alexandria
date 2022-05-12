from django.conf import settings
from django.db import models

from alexandria.utils.models import TimeStampMixin


class Receipt(TimeStampMixin):
    """
    Single receipt object.

    Each receipt is designed in https://receiptline.github.io/designer/
    (https://github.com/receiptline/receiptline) and they use the odd text
    formatting shown there. 

    """

    name = models.CharField(max_length=255)
    body = models.TextField(null=True, blank=True)
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)


class ReceiptContainer(TimeStampMixin):
    """
    Receipts are printed at the following four hard-coded events:

    - finishing checkout session
    - a hold is ready
      - for example, going onto the hold shelf for patron pickup
    - monetary transaction receipt
      - fines, book sales, replacing an item, etc.
    - transportation slip
      - going from one branch location to another
      - for example, a hold or entering a new item where the home location
          is not the work location of the person entering it
    """
    checkout_receipt = models.ForeignKey(
        Receipt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checkout_receipt",
    )
    hold_receipt = models.ForeignKey(
        Receipt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hold_receipt",
    )
    money_receipt = models.ForeignKey(
        Receipt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="money_receipt",
    )
    transport_receipt = models.ForeignKey(
        Receipt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transport_receipt",
    )
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)
