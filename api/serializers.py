"""Модуль с сериализаторами."""
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class AuthSerializer(TokenObtainPairSerializer):
    """Сериализатор для авторизации."""

    username_field = User.EMAIL_FIELD

    def validate(self, attrs: dict) -> dict:
        """Расширенный метод валидации."""
        attrs["email"] = attrs["email"].lower()
        return super().validate(attrs)
