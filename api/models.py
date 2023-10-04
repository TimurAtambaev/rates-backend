"""Модели приложения."""
from django.contrib.postgres import fields
from django.db import models
from django.contrib.auth.models import AbstractUser, User


class AppUser(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(verbose_name="email address", unique=True)
    currencies = fields.ArrayField(models.CharField,
                                   verbose_name="currencies")

    USERNAME_FIELD = User.EMAIL_FIELD
    REQUIRED_FIELDS = [User.USERNAME_FIELD]


class Rates(AbstractUser):
    """Модель котировок валют."""
    date = models.DateTimeField(verbose_name="current date")
    currencies = models.JSONField(verbose_name="currencies")
