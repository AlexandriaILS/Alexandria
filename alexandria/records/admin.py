from django.contrib import admin

from alexandria.records.models import Hold, Subject, Record, Item, Collection, ItemType, ItemTypeBase


class ItemAdmin(admin.ModelAdmin):
    ordering = ("record__title",)
    search_fields = ["record__title", "record__authors", "barcode", "call_number"]
    exclude = (
        "marc_leader",
        "content_type",
        "object_id",
    )

    readonly_fields = ("checked_out_to",)


class RecordAdmin(admin.ModelAdmin):
    ordering = ("title",)
    search_fields = ["searchable_title", "searchable_authors", "barcode", "call_number"]
    exclude = Record().get_searchable_field_names()


admin.site.register(Item, ItemAdmin)
admin.site.register(Subject)
admin.site.register(Record, RecordAdmin)
admin.site.register(Collection)
admin.site.register(ItemType)
admin.site.register(ItemTypeBase)
admin.site.register(Hold)
