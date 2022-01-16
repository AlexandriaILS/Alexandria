from django.urls import path
from django.contrib.auth import views as django_auth_views

from alexandria.catalog import views
from alexandria.catalog.authentication import views as auth_views
from alexandria.catalog.user_accounts import views as user_views

urlpatterns = [
    path("", views.index, name="homepage"),
    path("search/", views.search, name="search"),
    path("detail/<int:item_id>/", views.item_detail, name="item_detail"),
    # user_account views
    path("mycheckouts", user_views.my_checkouts, name="my_checkouts"),
    path("myholds", user_views.my_holds, name="my_holds"),
    path("myfees", user_views.my_fees, name="my_fees"),
    path("mysettings", user_views.SettingsView.as_view(), name="my_settings"),
    # authentication
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.logout_view, name="logout"),
    # many thanks to https://learndjango.com/tutorials/django-password-reset-tutorial
    path(
        "password_reset/",
        django_auth_views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        django_auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        django_auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        django_auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "password_change/",
        django_auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password_change/done/",
        django_auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
]
