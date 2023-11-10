"""Модуль путей приложения."""
from django.urls import path
from django.views.decorators.cache import cache_page

from api.views import AnaliticsView, Auth, RatesView, Registration
from rates.settings import CACHE_TIMEOUT

urlpatterns = [
    path("user/register/", Registration.as_view(), name="registration"),
    path("user/login/", Auth.as_view(), name="auth"),
    path("user_currency/", RatesView.as_view(), name="user_currency"),
    path("rates/", RatesView.as_view(), name="rates"),
    path(
        "currency/<int:id>/analytics/",
        cache_page(CACHE_TIMEOUT)(AnaliticsView.as_view()),
        name="analitics",
    ),
]
