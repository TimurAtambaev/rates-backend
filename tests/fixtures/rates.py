"""Фикстуры для тестов котировок валют."""
from datetime import datetime
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
    """Фабрика входных данных для тестов котировок валют."""

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


@pytest.fixture()
def rates_query_factory(
    currency_factory: Callable, rates_factory: Callable
) -> Callable[[dict[str, dict]], tuple]:
    """Фабрика набора котировок валют для тестов."""

    def _factory() -> tuple:
        currency = currency_factory(charcode="USD")
        rate_1 = rates_factory(
            charcode="USD",
            value=100,
            date=datetime.fromisoformat("2024-05-01").date(),
        )
        rate_2 = rates_factory(
            charcode="USD",
            value=200,
            date=datetime.fromisoformat("2024-05-07").date(),
        )
        rates_factory(
            charcode="USD",
            value=300,
            date=datetime.fromisoformat("2024-05-10").date(),
        )
        rates_factory(
            charcode="EUR",
            value=400,
            date=datetime.fromisoformat("2024-05-05").date(),
        )
        return currency, rate_1, rate_2

    return _factory


RatesQueryAssertion: TypeAlias = Callable[[list, str, Rates, Rates], None]


@pytest.fixture()
def assert_correct_rates() -> RatesQueryAssertion:
    """Проверка возвращения корректного набора валют с нужными параметрами."""

    def _check(
        response_rates: list,
        charcode: str,
        rate_1: Rates = None,
        rate_2: Rates = None,
    ) -> None:
        assert response_rates[0]["charcode"] == charcode
        assert response_rates[1]["charcode"] == charcode
        assert not response_rates[0]["is_threshold_exceeded"]
        assert response_rates[1]["is_threshold_exceeded"]

        if threshold_match_type := response_rates[0].get(
            "threshold_match_type"
        ):
            assert threshold_match_type == "less"
        if percentage_ratio := response_rates[0].get("percentage_ratio"):
            assert (
                percentage_ratio
                == str(round(100 * rate_1.value / 150, 2)) + "%"
            )
        if threshold_match_type := response_rates[1].get(
            "threshold_match_type"
        ):
            assert threshold_match_type == "exceeded"
        if percentage_ratio := response_rates[1].get("percentage_ratio"):
            assert (
                percentage_ratio
                == str(round(100 * rate_2.value / 150, 2)) + "%"
            )
        if is_min_value := response_rates[0].get("is_min_value"):
            assert is_min_value is True
        if is_max_value := response_rates[1].get("is_max_value"):
            assert is_max_value is True

    return _check
