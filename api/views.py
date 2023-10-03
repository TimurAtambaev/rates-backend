"""Модуль с обработчиками запросов."""
from typing import Any
from django.db import transaction
from loguru import logger
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.forms import AuthRegForm
from api.models import User
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
        """Запрос для регистрации."""
        data = AuthRegForm(request.data)
        if not data.is_valid():
            return Response(
                {"errors": data.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            with transaction.atomic():
                user = User.objects.create(**data.cleaned_data)
                user.set_password(data.cleaned_data["password"])
                user.save(update_fields=["password"])
        except Exception as exc:
            logger.error(exc)
            raise exc
        return Response("Registration successfully completed")


class Auth(TokenObtainPairView):
    """Класс авторизации через email."""

    renderer_classes = [JSONRenderer]
    serializer_class = AuthSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Проверка данных для авторизации."""
        data = AuthRegForm(request.data)
        if not data.is_valid():
            return Response(
                {"errors": data.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        return super().post(request, *args, **kwargs)
