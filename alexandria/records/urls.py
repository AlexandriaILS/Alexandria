from django.urls import path

from alexandria.records.views import holds

urlpatterns = [
    path(
        "placehold/record/<int:item_id>/<int:item_type_id>/<int:location_id>/",
        holds.place_hold_on_record,
        name="place_hold_on_record",
    ),
    path(
        "placehold/item/<int:item_id>/<int:item_type_id>/<int:location_id>/",
        holds.place_hold_on_item,
        name="place_hold_on_item",
    ),
    path(
        "renewhold/<int:item_id>/",
        holds.renew_hold_on_item,
        name="renew_hold_on_item",
    ),
    path("deletehold/<int:hold_id>/", holds.delete_hold, name="delete_hold"),
]
