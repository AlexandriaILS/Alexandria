from django.urls import path
from holds import views

urlpatterns = [
    path(
        "placehold/record/<int:item_id>/<int:item_type_id>/",
        views.place_hold_on_record,
        name="place_hold",
    ),
    path(
        "placehold/item/<int:item_id>/<int:item_type_id>/",
        views.place_hold_on_item,
        name="place_hold",
    ),
]
