"""Модуль с тестами котировок валют."""
from decimal import Decimal
from http import HTTPStatus
from typing import Callable, Optional

import pytest
from django.test import Client
from django.urls import reverse

from tests.fixtures.rates import RatesAssertion, RatesData, RatesQueryAssertion


@pytest.mark.django_db()
def test_add_rates_unauthorized(
    client: Client,
    currency_factory: Callable,
    rates_data_factory: Callable[[int, Optional[int]], RatesData],
) -> None:
    """Тест запроса на добавление валюты неавторизованным пользователем."""
    currency = currency_factory()
    rates_data = rates_data_factory(currency.id)
    response = client.post(reverse("rates"), data=rates_data)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db()
def test_add_rates(
    client: Client,
    user_token: Callable,
    currency_factory: Callable,
    rates_data_factory: Callable[[int, Optional[int]], RatesData],
    assert_correct_add_rate: RatesAssertion,
) -> None:
    """Тест добавления валюты в список отслеживаемых."""
    user, token = user_token()
    currency = currency_factory()
    rates_data = rates_data_factory(currency.id)
    response = client.post(
        reverse("rates"),
        data=rates_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert_correct_add_rate(currency.charcode, user, rates_data)


@pytest.mark.django_db()
def test_get_rates_unauthorized(
    client: Client,
    rates_factory: Callable,
) -> None:
    """Тест получения котировок валют неавторизованным пользователем."""
    rate = rates_factory()
    response = client.get(reverse("rates"))
    assert response.status_code == HTTPStatus.OK
    assert response.json()["rates"][0]["id"] == rate.id
    assert response.json()["rates"][0]["charcode"] == rate.charcode
    assert Decimal(response.json()["rates"][0]["value"]) == rate.value


@pytest.mark.parametrize(("order_by", "value"), [("", 100), ("-value", 200)])
@pytest.mark.django_db()
def test_sort_rate(
    client: Client,
    rates_factory: Callable,
    order_by: Optional[str],
    value: int,
) -> None:
    """Тест сортировки котировок валют."""
    rates_factory(value=200)
    rates_factory(value=100)
    response = client.get(reverse("rates"), data={"order_by": order_by})
    assert response.status_code == HTTPStatus.OK
    assert Decimal(response.json()["rates"][0]["value"]) == value


@pytest.mark.django_db()
def test_get_rates_authorized(
    client: Client,
    user_token: Callable,
    rates_query_factory: Callable,
    user_currency_factory: Callable,
    assert_correct_rates: RatesQueryAssertion,
) -> None:
    """Тест получения списка котировок валют авторизованным пользователем."""
    user, token = user_token()
    rates_query_factory()
    user_currency = user_currency_factory(
        user=user, charcode="USD", threshold=150
    )
    response = client.get(
        reverse("rates"), headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["rates"]) == 3
    assert_correct_rates(response.json()["rates"], user_currency.charcode)


@pytest.mark.django_db()
def test_get_currencies(
    client: Client,
    currency_factory: Callable,
) -> None:
    """Тест получения всех валют."""
    currency = currency_factory()
    for _ in range(3):
        currency_factory()
    response = client.get(reverse("currencies"))
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["currencies"]) == 4
    assert response.json()["currencies"][str(currency.id)] == currency.charcode
