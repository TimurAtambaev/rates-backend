"""Модуль с обработчиками запросов."""
from datetime import datetime
from typing import Any

from django.http import JsonResponse
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

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
from api.serializers import (
    AuthSerializer,
    RatesSerializer,
    RegistrationSerializer,
)


class Registration(APIView):
    """Класс регистрации через email."""

    @extend_schema(request=RegistrationSerializer, responses={201: None})
    def post(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """Регистрация пользователя."""
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            create_user(serializer.data)
        except Exception as exc:
            return Response(
                {"errors": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_201_CREATED)


class Auth(TokenObtainPairView):
    """Класс авторизации через email."""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Получение токена аутентификации по email и password."""
        serializer = AuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().post(request, *args, **kwargs)


class RatesView(APIView):
    """Класс для работы с котировками."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        request=RatesSerializer,
        responses={
            201: None,
            400: inline_serializer(
                name="WrongQueryParams",
                fields={"errors": serializers.CharField()},
            ),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Добавление котируемой валюты в список отслеживаемых.

        С установкой порогового значения.
        """
        serializer = RatesSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (currency := get_currency(serializer.data["currency"])):
            return Response(
                {
                    "errors": "currency with this ID not found, use "
                    "endpoint 'currency/all/' to obtain all available "
                    "currencies"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        create_or_update_user_currency(
            request.user, currency.charcode, serializer.data["threshold"]
        )

        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="order_by",
                description="value или -value",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: inline_serializer(
                name="TrackableRates",
                fields={"rates": serializers.ListField()},
            )
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> JsonResponse:
        """Получение списка актуальных котировок."""
        order_by = get_order_by(request.GET.get("order_by"))

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
            rate["is_threshold_exceeded"] = (
                rate["value"] > user_currencies_dict[rate["charcode"]]
            )
        return JsonResponse({"rates": trackable_rates})


class AnaliticsView(APIView):
    """Класс для работы с аналитикой котировок."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="threshold",
                description="Пороговое значение котировки",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="date_from",
                description="Дата от",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="date_to", description="Дата до", required=True, type=str
            ),
            OpenApiParameter(
                name="order_by",
                description="value или -value",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: inline_serializer(
                name="TargetRates", fields={"rates": serializers.ListField()}
            ),
            404: inline_serializer(
                name="CurrencyNotFound",
                fields={"errors": serializers.CharField()},
            ),
            400: inline_serializer(
                name="WrongQueryParams",
                fields={"errors": serializers.CharField()},
            ),
        },
    )
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
                {
                    "errors": "currency with this ID not found, use "
                    "endpoint 'currency/all/' to obtain all available "
                    "currencies"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        for query_param in (
            "threshold",
            "date_from",
            "date_to",
        ):  # обязательные параметры запроса на аналитику
            if not request.GET.get(query_param):
                return JsonResponse(
                    {"errors": f"'{query_param}' required in query params"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            threshold = int(request.GET.get("threshold"))
            date_from = datetime.fromisoformat(
                request.GET.get("date_from")
            ).date()
            date_to = datetime.fromisoformat(request.GET.get("date_to")).date()
        except Exception as exc:
            return JsonResponse(
                {"errors": f"please check query params: '{exc}'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order_by = get_order_by(request.GET.get("order_by"))

        target_rates = list(
            get_filter_by_code_and_period_rates(
                target_currency.charcode, date_from, date_to, order_by
            )
        )

        add_analytics_fields(target_rates, threshold, order_by)

        return JsonResponse({"rates": target_rates})


class CurrencyView(APIView):
    """Класс для работы с валютами."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        responses={
            200: inline_serializer(
                name="AllCurrencies",
                fields={"currencies": serializers.DictField()},
            )
        }
    )
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


def add_analytics_fields(
    target_rates: list, threshold: int, order_by: str
) -> None:
    """Добавление полей с аналитикой валют."""
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


def get_order_by(order_by: str) -> str:
    """Определить порядок сортировки по полю value."""
    return order_by if order_by == "-value" else "value"
