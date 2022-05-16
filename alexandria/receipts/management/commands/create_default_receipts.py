from django.conf import settings
from django.core.management.base import BaseCommand

from alexandria.receipts.models import Receipt, ReceiptContainer

# TODO: finish replacing placeholder data with actual variable references
CHECKOUT_RECEIPT = """
^^^Checkouts^^^

{width:*,12; text:nowrap; align:center}
|Title | Due Date|
-
{% for item in items %}
|{{item.record.title}} | {{ item.get_due_date }}|
{% endfor %}
{width:auto; align:center}

Renew your materials and place holds online or
by phone:

https://neverlandlibrary.lib.in.us
(317) 555-1234

{border:line}
You've saved "$4831.20" by using your library
card! Nice work!
{border:none}

"Neverland Library"
123 Main St
Indianapolis, IN 46227
(317) 555-1234
Sunday, April 8 2022 @ 11:17pm

=
"""

HOLD_RECEIPT = """

^^^^12345678912345^^^^





|Title: item.record.title
|Item Barcode:

{c:item.barcode}

|Hold Expiry: 5/13/2022

=
"""

TRANSPORT_RECEIPT = """
Transport to
^^^^Central Branch^^^^





|Title: item.record.title
|Item Barcode:

{c:item.barcode}

=
"""

MONETARY_RECEIPT = """
^^^^Receipt^^^^

{width:*,12; text:nowrap; align:center}
|Description | Amount|
-
|Book Purchase | $3.00|
|Book Purchase | $2.00|
|Book Purchase | $2.50|
|Fine | $0.25|

{% for item in items %}
|{{item.record.title}} | {{ item.get_due_date }}|
{% endfor %}
{width:auto; align:center}
-

Renew your materials and place holds online or
by phone:

https://neverlandlibrary.lib.in.us
(317) 555-1234

"Neverland Library"
123 Main St
Indianapolis, IN 46227
(317) 555-1234
Sunday, April 8 2022 @ 11:17pm

=
"""


class Command(BaseCommand):
    help = "Creates the four base receipts for an example site."

    def handle(self, *args, **options):
        checkout, _ = Receipt.objects.get_or_create(
            name="Default Checkout Receipt", body=CHECKOUT_RECEIPT
        )
        hold, _ = Receipt.objects.get_or_create(
            name="Default Hold Receipt", body=HOLD_RECEIPT
        )
        monetary, _ = Receipt.objects.get_or_create(
            name="Default Monetary Receipt", body=MONETARY_RECEIPT
        )
        transport, _ = Receipt.objects.get_or_create(
            name="Default Transport Receipt", body=TRANSPORT_RECEIPT
        )
        container, _ = ReceiptContainer.objects.get_or_create(
            host=settings.DEFAULT_HOST_KEY
        )
        container.checkout_receipt = checkout
        container.hold_receipt = hold
        container.money_receipt = monetary
        container.transport_receipt = transport
        container.save()

        self.stdout.write("Default system receipts created!")
