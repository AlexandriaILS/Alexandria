from django.urls import path

from alexandria.catalog.printing import views

urlpatterns = [
    path("generate_receipt/", views.generate_receipt, name="generate_receipt"),
    path("", views.index),
]
