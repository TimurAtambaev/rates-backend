"""Модуль с обработчиками запросов."""
from datetime import datetime
from typing import Any

from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from api.forms import AuthRegForm, RatesForm
from api.repository import (
    create_or_update_user_currency,
    create_user,
    get_all_currencies,
    get_all_rates,
    get_currency,
    get_filter_by_code_and_period_rates,
    get_filter_by_code_rates,
    get_user_currencies,
)
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

        create_user(data)

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
        if not (currency := get_currency(form.cleaned_data["currency"])):
            return Response(
                {"errors": "currency with this ID was not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        create_or_update_user_currency(
            request.user, currency.charcode, form.cleaned_data["threshold"]
        )

        return Response(status=status.HTTP_201_CREATED)

    def get(self, request: Request, *args: Any, **kwargs: Any) -> JsonResponse:
        """Получение списка актуальных котировок."""
        order_by = (
            request.GET.get("order_by")
            if request.GET.get("order_by") == "-value"
            else "value"
        )
        if not request.user.is_authenticated:
            return JsonResponse({"rates": list(get_all_rates(order_by))})

        user_currencies = get_user_currencies(request.user.id)
        user_currencies_dict = {
            currency.charcode: currency.threshold
            for currency in user_currencies
        }
        trackable_rates = list(
            get_filter_by_code_rates(user_currencies_dict, order_by)
        )
        for rate in trackable_rates:
            for currency in user_currencies_dict:
                if rate["charcode"] == currency:
                    rate["is_threshold_exceeded"] = (
                        rate["value"] > user_currencies_dict[currency]
                    )
        return JsonResponse({"rates": trackable_rates})


class AnaliticsView(APIView):
    """Класс для работы с аналитикой котировок."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(
        self,
        request: Request,
        id: int,  # noqa A002
        *args: Any,
        **kwargs: Any,
    ) -> JsonResponse:
        """Получение аналитических данных по котирумой валюте за период."""
        if not (target_currency := get_currency(id)):
            return JsonResponse(
                {"errors": "currency with this ID was not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (threshold := request.GET.get("threshold")):
            return JsonResponse(
                {"errors": "missing 'threshold' in query params"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (date_from := request.GET.get("date_from")):
            return JsonResponse(
                {"errors": "missing 'date_from' in query params"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (date_to := request.GET.get("date_to")):
            return JsonResponse(
                {"errors": "missing 'date_to' in query params"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            threshold = int(threshold)
            date_from = datetime.fromisoformat(date_from).date()
            date_to = datetime.fromisoformat(date_to).date()
        except Exception as exc:
            return JsonResponse(
                {"errors": f"wrong query params: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order_by = (
            request.GET.get("order_by")
            if request.GET.get("order_by") == "-value"
            else "value"
        )

        target_rates = list(
            get_filter_by_code_and_period_rates(
                target_currency.charcode, date_from, date_to, order_by
            )
        )
        for num, rate in enumerate(target_rates, start=1):
            rate["percentage_ratio"] = (
                str(round(100 * rate["value"] / threshold, 2)) + "%"
            )
            if rate["value"] > threshold:
                rate["is_threshold_exceeded"] = True
                rate["threshold_match_type"] = "exceeded"
            elif rate["value"] < threshold:
                rate["is_threshold_exceeded"] = False
                rate["threshold_match_type"] = "less"
            elif rate["value"] == threshold:
                rate["is_threshold_exceeded"] = False
                rate["threshold_match_type"] = "equal"

            rate["is_min_value"] = bool(
                num == 1
                and order_by == "value"
                or num == len(target_rates)
                and order_by == "-value"
            )
            rate["is_max_value"] = bool(
                num == len(target_rates)
                and order_by == "value"
                or num == 1
                and order_by == "-value"
            )

        return JsonResponse({"rates": target_rates})


class CurrencyView(APIView):
    """Класс для работы с валютами."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> JsonResponse:
        """Получение всех валют."""
        return JsonResponse(
            {
                "currencies": {
                    currency.id: currency.charcode
                    for currency in get_all_currencies()
                }
            }
        )
