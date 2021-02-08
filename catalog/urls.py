from django.urls import path

from catalog import views

urlpatterns = [
    path("", views.index, name="homepage"),
    path("search/", views.search, name="search"),
    path("add_from_loc/", views.add_from_loc, name="add_from_loc"),
]
