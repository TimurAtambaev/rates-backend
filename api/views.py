"""Модуль с обработчиками запросов."""
from datetime import datetime
from typing import Any

from django.db import transaction
from django.http import JsonResponse
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

        with transaction.atomic():
            data.cleaned_data["username"] = data.cleaned_data["email"]
            user = AppUser.objects.create(**data.cleaned_data)
            user.set_password(data.cleaned_data["password"])
            user.save(update_fields=["password"])

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
            currency := Currency.objects.filter(
                id=form.cleaned_data["currency"]
            ).first()
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
        order_by = (
            request.GET.get("order_by")
            if request.GET.get("order_by") == "-value"
            else "value"
        )
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    "rates": list(
                        Rates.objects.order_by(order_by)
                        .all()
                        .values("id", "date", "charcode", "value")
                    )
                }
            )

        user_currencies = UserCurrency.objects.filter(user__id=request.user.id)
        user_currencies_dict = {
            currency.charcode: currency.threshold
            for currency in user_currencies
        }
        trackable_rates = list(
            Rates.objects.order_by(order_by)
            .filter(charcode__in=user_currencies_dict)
            .values("id", "date", "charcode", "value")
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
        if not (target_currency := Currency.objects.filter(id=id).first()):
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
            Rates.objects.order_by(order_by)
            .filter(charcode=target_currency.charcode)
            .filter(date__gte=date_from)
            .filter(date__lte=date_to)
            .values("id", "date", "charcode", "value")
        )
        for num, rate in enumerate(target_rates, start=1):
            if rate["charcode"] == target_currency.charcode:
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
