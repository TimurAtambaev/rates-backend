"""Модуль с обработчиками запросов."""
from typing import Any

from django.db import transaction
from django.http import JsonResponse
from loguru import logger
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from api.forms import AuthRegForm, RatesForm
from api.models import AppUser, Currency, Rates, UserCurrency
from api.serializers import AuthSerializer


class Registration(APIView):
    """Класс регистрации через email."""

    def post(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """Регистрация и активация пользователя."""
        data = AuthRegForm(request.data)
        if not data.is_valid():
            return Response(
                {"errors": data.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            with transaction.atomic():
                data.cleaned_data["username"] = data.cleaned_data["email"]
                user = AppUser.objects.create(**data.cleaned_data)
                user.set_password(data.cleaned_data["password"])
                user.save(update_fields=["password"])
        except Exception as exc:
            logger.error(exc)
            raise exc
        return Response(status=status.HTTP_201_CREATED)


class Auth(TokenObtainPairView):
    """Класс авторизации через email."""

    serializer_class = AuthSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Получение токена аутентификации по email и password."""
        form = AuthRegForm(request.data)
        form.data["username"] = form.data["email"]
        if not form.is_valid():
            return Response(
                {"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return super().post(request, *args, **kwargs)


class RatesView(APIView):
    """Класс для работы с котировками."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Добавление котируемой валюты в список отслеживаемых.

        С установкой порогового значения.
        """
        form = RatesForm(request.data)
        if not form.is_valid():
            return Response(
                {"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        if not (
            currency := Currency.objects.get(id=form.cleaned_data["currency"])
        ):
            return Response(
                {"errors": "currency with this ID was not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        UserCurrency.objects.update_or_create(
            user=request.user,
            charcode=currency.charcode,
            threshold=form.cleaned_data["threshold"],
        )

        return Response(status=status.HTTP_201_CREATED)

    def get(self, request: Request, *args: Any, **kwargs: Any) -> JsonResponse:
        """Получение списка актуальных котировок."""
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    "rates": list(
                        Rates.objects.all().values(
                            "id", "date", "charcode", "value"
                        )
                    )
                }
            )

        user_currencies = UserCurrency.objects.filter(user__id=request.user.id)
        user_currencies_dict = {
            currency.charcode: currency.threshold
            for currency in user_currencies
        }
        trackable_rates = Rates.objects.filter(
            charcode__in=user_currencies_dict
        )
        for rate in trackable_rates:
            for currency in user_currencies_dict:
                if rate.charcode == currency:
                    trackable_rates.is_threshold_exceeded = (
                        rate.value > user_currencies_dict[currency]
                    )
        return JsonResponse(
            {
                "rates": list(
                    trackable_rates.values("id", "date", "charcode", "value")
                )
            }
        )
