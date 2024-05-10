"""Модуль с сериализаторами."""
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationSerializer(serializers.Serializer):
    """Сериализатор входных данных регистрации."""

    email = serializers.EmailField(required=True, max_length=200)
    password = serializers.CharField(
        required=True, min_length=8, max_length=50
    )
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)


class AuthSerializer(TokenObtainPairSerializer):
    """Сериализатор авторизации."""

    username_field = User.EMAIL_FIELD

    email = serializers.EmailField(required=True, max_length=200)
    password = serializers.CharField(
        required=True, min_length=8, max_length=50
    )

    def validate(self, attrs: dict) -> dict:
        """Расширенный метод валидации."""
        attrs["email"] = attrs["email"].lower()
        return super().validate(attrs)


class RatesSerializer(serializers.Serializer):
    """Сериализатор добавления валют."""

    currency = serializers.IntegerField()
    threshold = serializers.IntegerField()
