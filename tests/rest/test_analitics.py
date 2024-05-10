"""Модуль с тестами аналитики валют."""
from http import HTTPStatus
from typing import Callable

import pytest
from django.test import Client
from django.urls import reverse

from tests.fixtures.rates import RatesQueryAssertion


@pytest.mark.django_db()
def test_get_analitics_bad_request(
    client: Client,
    user_token: Callable,
    currency_factory: Callable,
) -> None:
    """Тест получения аналитических данных с неверными параметрами запроса."""
    currency = currency_factory()
    response = client.get(reverse("analitics", kwargs={"id": currency.id + 1}))
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = client.get(reverse("analitics", kwargs={"id": currency.id}))
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["errors"] == "'threshold' required in query params"


@pytest.mark.django_db()
def test_get_analitics(
    client: Client,
    user_token: Callable,
    rates_query_factory: Callable,
    assert_correct_rates: RatesQueryAssertion,
) -> None:
    """Тест получения аналитических данных по валюте."""
    currency, rate_1, rate_2 = rates_query_factory()
    response = client.get(
        reverse("analitics", kwargs={"id": currency.id}),
        data={
            "threshold": 150,
            "date_from": "2024-05-01",
            "date_to": "2024-05-08",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()["rates"]) == 2
    assert_correct_rates(
        response.json()["rates"], currency.charcode, rate_1, rate_2
    )
