from django.contrib import admin

from catalog.models import Subject, Record, Item, Collection


class ItemAdmin(admin.ModelAdmin):
    ordering = ("record__title",)
    search_fields = ["record__title", "record__authors"]
    exclude = (
        "marc_leader",
        "content_type",
        "object_id",
    )

    readonly_fields = (
        "checked_out_to",
    )


admin.site.register(Item, ItemAdmin)
admin.site.register(Subject)
admin.site.register(Record)
admin.site.register(Collection)
