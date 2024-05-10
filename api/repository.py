"""Модуль с запросами в базу данных."""
import decimal
from datetime import date
from typing import Iterable, Optional

from django.db import transaction

from api.models import AppUser, Currency, Rates, UserCurrency


def create_user(data: dict) -> None:
    """Создать нового пользователя."""
    with transaction.atomic():
        data["username"] = data["email"]
        user = AppUser.objects.create(**data)
        user.set_password(data["password"])
        user.save(update_fields=["password"])


def get_all_currencies() -> Iterable:
    """Получить все валюты."""
    return Currency.objects.all()


def get_currency(currency_id: int) -> Optional[Currency]:
    """Получить валюту по id."""
    return Currency.objects.filter(id=currency_id).first()


def create_or_update_currency(charcode: str) -> None:
    """Создать или обновить валюту."""
    Currency.objects.update_or_create(charcode=charcode)


def create_or_update_user_currency(
    user: AppUser, charcode: str, threshold: int
) -> None:
    """Создать или обновить отслеживаемую валюту пользователя."""
    UserCurrency.objects.update_or_create(
        user=user,
        charcode=charcode,
        threshold=threshold,
    )


def get_user_currencies(user_id: int) -> Iterable:
    """Получить отслеживаемые валюты пользователя."""
    return UserCurrency.objects.filter(user__id=user_id)


def create_rate(date: date, charcode: str, value: decimal) -> None:
    """Создать котировку валюты."""
    Rates.objects.create(date=date, charcode=charcode, value=value)


def get_all_rates(order_by: str) -> Iterable:
    """Получить котировки всех валют."""
    return (
        Rates.objects.order_by(order_by)
        .all()
        .values("id", "date", "charcode", "value")
    )


def get_filter_by_code_rates(currencies_dict: dict, order_by: str) -> Iterable:
    """Получить котировки валют отфильтрованные по коду."""
    return (
        Rates.objects.order_by(order_by)
        .filter(charcode__in=currencies_dict)
        .values("id", "date", "charcode", "value")
    )


def get_filter_by_code_and_period_rates(
    charcode: str, date_from: date, date_to: date, order_by: str
) -> Iterable:
    """Получить котировки валют отфильтрованные по коду и периоду."""
    return (
        Rates.objects.order_by(order_by)
        .filter(charcode=charcode)
        .filter(date__gte=date_from)
        .filter(date__lte=date_to)
        .values("id", "date", "charcode", "value")
    )


def get_filter_by_code_and_date_rates(charcode: str, date: date) -> Iterable:
    """Получить котировки валют отфильтрованные по коду и дате."""
    return Rates.objects.filter(date=date, charcode=charcode)
