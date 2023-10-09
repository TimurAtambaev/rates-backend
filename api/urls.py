"""Модуль путей приложения."""
from django.urls import path

from api.models import Rates
from api.views import Registration, Auth

urlpatterns = [
    path("user/register/", Registration.as_view(), name="registration"),
    path("user/login/", Auth.as_view(), name="auth"),
    # path("rates/", Rates.as_view(), name="rates"),
]
