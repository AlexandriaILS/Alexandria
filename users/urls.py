from django.urls import path
from django.contrib.auth import views as auth_views

from users import views

urlpatterns = [
    path("mycheckouts", views.my_checkouts, name="my_checkouts"),
    path("myholds", views.my_holds, name="my_holds"),
    path("myfees", views.my_fees, name="my_fees"),
    path("mysettings", views.SettingsView.as_view(), name="my_settings"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("password_reset/", auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]
