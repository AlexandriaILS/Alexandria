from django.urls import path

from catalog import views

urlpatterns = [
    path("", views.index, name="homepage"),
    path("search/", views.search, name="search"),
    path("detail/<int:item_id>", views.item_detail, name="item_detail"),
    path("add_from_loc/", views.add_from_loc, name="add_from_loc"),
    path(
        "placehold/<int:item_id>/<int:item_type_id>/",
        views.place_hold,
        name="place_hold",
    ),
    path(
        "add_marc_from_loc/",
        views.import_marc_record_from_loc,
        name="add_marc_from_loc",
    ),
]
