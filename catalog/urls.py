from django.urls import path
from catalog import views

urlpatterns = [
    path("", views.index, name="homepage"),
    path("search/", views.search, name="search"),
    path("detail/<int:item_id>/", views.item_detail, name="item_detail"),
]
