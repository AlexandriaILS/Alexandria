from django.urls import path

from users import views

urlpatterns = [
    path("mycheckouts", views.my_checkouts, name="my_checkouts"),
    path("myholds", views.my_holds, name="my_holds"),
    path("myfees", views.my_fees, name="my_fees"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
]
