from django.urls import path
from staff import views

urlpatterns = [
    path("", views.index, name="staff_index"),
    path("search", views.staff_search, name="staff_search"),
]
