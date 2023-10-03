"""Модуль с сериализаторами."""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api.models import User


class AuthSerializer(TokenObtainPairSerializer):
    """Сериализатор для авторизации."""
    username_field = User.EMAIL_FIELD

    def validate(self, attrs: dict) -> dict:
        """Валидация и аутентификация по email и password."""
        attrs["email"] = attrs["email"].lower()
        data = {}
        user = User.objects.filter(email=attrs["email"]).first()
        if not user:
            return data
        refresh = self.get_token(user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data
