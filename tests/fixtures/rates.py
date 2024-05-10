"""Фикстуры для тестов котировок валют."""
from typing import Callable, Optional, TypeAlias, TypedDict

import pytest
from django_fakery import factory
from mimesis import Numeric

from api.models import AppUser, Currency, Rates, UserCurrency


class RatesData(TypedDict, total=False):
    """Класс тестовых данных добавления котировок валют."""

    currency: int
    threshold: int


@pytest.fixture()
def rates_data_factory() -> Callable[[int | None, int | None], RatesData]:
    """Фабрика данных для тестов котировок валют."""

    def _factory(
        currency_id: Optional[int] = None, threshold: Optional[int] = None
    ) -> RatesData:
        return {
            "currency": currency_id or Numeric().increment(),
            "threshold": threshold or Numeric().increment(),
        }

    return _factory


@pytest.fixture()
def currency_factory() -> Callable[[], Currency]:
    """Фабрика валют."""

    def _factory(**fields: dict) -> Currency:
        return factory.make(Currency, fields={**fields})

    return _factory


@pytest.fixture()
def rates_factory() -> Callable[[], Currency]:
    """Фабрика котировок валют."""

    def _factory(**fields: dict) -> Currency:
        return factory.make(Rates, fields={**fields})

    return _factory


@pytest.fixture()
def user_currency_factory() -> Callable[[], Currency]:
    """Фабрика котировок валют отслеживаемых пользователем."""

    def _factory(**fields: dict) -> Currency:
        return factory.make(UserCurrency, fields={**fields})

    return _factory


RatesAssertion: TypeAlias = Callable[[str, AppUser, RatesData], None]


@pytest.fixture()
def assert_correct_add_rate() -> RatesAssertion:
    """Проверка корректного добавления валюты в список отслеживаемых."""

    def _check(charcode: str, user: AppUser, rates_data: RatesData) -> None:
        user_currency = UserCurrency.objects.filter(charcode=charcode).first()
        assert user_currency
        assert user_currency.user == user
        assert user_currency.threshold == rates_data["threshold"]

    return _check
