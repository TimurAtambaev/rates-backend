"""Модуль с обработчиками запросов."""
from typing import Any

from django.db import transaction
from loguru import logger
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.forms import AuthRegForm
from api.models import AppUser
from api.serializers import AuthSerializer


class Registration(APIView):
    """Класс регистрации через email."""

    renderer_classes = [JSONRenderer]

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
        return Response("Registration successfully completed",
                        status=status.HTTP_201_CREATED)


class Auth(TokenObtainPairView):
    """Класс авторизации через email."""

    renderer_classes = [JSONRenderer]
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
