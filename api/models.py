"""Модели приложения."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=150, blank=True, null=True, unique=True)
