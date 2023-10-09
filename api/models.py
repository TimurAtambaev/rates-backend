"""Модели приложения."""
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import AbstractUser, User

from rates import settings


class AppUser(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(verbose_name="email address", unique=True)
    currencies = ArrayField(models.CharField(max_length=10),
                                   verbose_name="currencies",
                                   blank=True,
                                   null=True)
    threshold = models.DecimalField(verbose_name="threshold",
                                    max_digits=settings.MAX_DIGITS,
                                    decimal_places=settings.DECIMAL_PLACES,
                                    blank=True,
                                    null=True)

    USERNAME_FIELD = User.EMAIL_FIELD
    REQUIRED_FIELDS = [User.USERNAME_FIELD]

    def __str__(self):
        return self.email


class Rates(models.Model):
    """Модель котировок валют."""
    date = models.DateField(verbose_name="date")
    currencies = models.JSONField(verbose_name="currencies")

    def __str__(self):
        return self.date
