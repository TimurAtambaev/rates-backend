"""Модуль путей приложения."""
from django.urls import path

from api.views import Registration, Auth

urlpatterns = [
    path("registration/", Registration.as_view(), name="registration"),
    path("auth/", Auth.as_view(), name="auth"),
]
