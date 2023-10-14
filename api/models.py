"""Модели приложения."""
from django.contrib.auth.models import AbstractUser, User
from django.db import models

from rates.settings import DECIMAL_PLACES, MAX_CURRENCY_CHARCODE, MAX_DIGITS


class Currency(models.Model):
    """Модель всех валют."""

    charcode = models.CharField(max_length=MAX_CURRENCY_CHARCODE)


class AppUser(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(verbose_name="email address", unique=True)

    USERNAME_FIELD = User.EMAIL_FIELD
    REQUIRED_FIELDS = [User.USERNAME_FIELD]

    def __str__(self) -> str:
        """Строковое представление модели."""
        return self.email


class UserCurrency(models.Model):
    """Модель валют отслеживаемых пользователем."""

    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    charcode = models.CharField(max_length=MAX_CURRENCY_CHARCODE)
    threshold = models.IntegerField()


class Rates(models.Model):
    """Модель котировок валют."""

    date = models.DateTimeField(verbose_name="date")
    charcode = models.CharField(max_length=MAX_CURRENCY_CHARCODE)
    value = models.DecimalField(
        max_digits=MAX_DIGITS, decimal_places=DECIMAL_PLACES
    )
