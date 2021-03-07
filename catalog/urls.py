from django.urls import path
from catalog import views

urlpatterns = [
    path("", views.index, name="homepage"),
    path("search/", views.search, name="search"),
    path("detail/<int:item_id>/", views.item_detail, name="item_detail"),
    path("edit/<int:item_id>/", views.ItemEdit.as_view(), name="item_edit"),
    path("add_from_loc/", views.add_from_loc, name="add_from_loc"),
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
    path(
        "add_marc_from_loc/",
        views.import_marc_record_from_loc,
        name="add_marc_from_loc",
    ),
]
