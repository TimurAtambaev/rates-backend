"""Модуль с сериализаторами."""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api.models import User


class AuthSerializer(TokenObtainPairSerializer):
    """Сериализатор для авторизации."""
    username_field = User.EMAIL_FIELD

    def validate(self, attrs: dict) -> dict:
        """Расширенный метод валидации."""
        attrs["email"] = attrs["email"].lower()
        return super().validate(attrs)
