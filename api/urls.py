"""Модуль путей приложения."""
from django.urls import path

from api.views import Auth, RatesView, Registration

urlpatterns = [
    path("user/register/", Registration.as_view(), name="registration"),
    path("user/login/", Auth.as_view(), name="auth"),
    path("user_currency/", RatesView.as_view(), name="user_currency"),
    path("rates/", RatesView.as_view(), name="rates"),
]
