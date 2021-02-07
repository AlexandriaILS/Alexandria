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
        "type",
        "human_readable_type",
        "bibliographic_level",
        "human_readable_bibliographic_level",
        "checked_out_to"
    )
    custom_fieldsets = [
        ("Checkout Info", {'fields': ['checked_out_to']}),
        ("Type of material", {"fields": ["type", "human_readable_type"]}),
        (
            "Bibliographic Info",
            {"fields": ["bibliographic_level", "human_readable_bibliographic_level"]},
        ),
    ]

    def get_fieldsets(self, request, obj=None):
        fs = super().get_fieldsets(request, obj)
        # fs now contains [(None, {'fields': fields})]
        fs[0][1]["fields"] = [
            f for f in fs[0][1]["fields"] if f not in self.readonly_fields
        ]
        fs += self.custom_fieldsets
        return fs


admin.site.register(Item, ItemAdmin)
admin.site.register(Subject)
admin.site.register(Record)
admin.site.register(Collection)
