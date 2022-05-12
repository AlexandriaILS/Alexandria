from django.contrib import admin

from alexandria.receipts.models import Receipt, ReceiptContainer

# Register your models here.
admin.site.register(Receipt)
admin.site.register(ReceiptContainer)
