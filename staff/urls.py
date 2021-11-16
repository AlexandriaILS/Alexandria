from django.urls import path, include
from staff import views
from staff.printing.urls import urlpatterns as printing_urls

urlpatterns = [
    path("", views.index, name="staff_index"),
    path("search/", views.staff_search, name="staff_search"),
    path("printing/", include(printing_urls)),
]
