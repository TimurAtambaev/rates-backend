"""Модуль с тестами регистрации и авторизации."""
from http import HTTPStatus
from typing import Callable

import pytest
from django.test import Client
from django.urls import reverse

from tests.fixtures.registration import RegistrationData, UserAssertion


@pytest.mark.django_db()
def test_valid_registration(
    client: Client,
    registration_data_factory: Callable[[], RegistrationData],
    assert_correct_registration: UserAssertion,
) -> None:
    """Тест регистрации пользователей."""
    registration_data = registration_data_factory()
    response = client.post(reverse("registration"), data=registration_data)
    assert response.status_code == HTTPStatus.CREATED
    assert_correct_registration(registration_data["email"], registration_data)


@pytest.mark.django_db()
def test_not_valid_registration(
    client: Client,
    registration_data_factory: Callable[[], RegistrationData],
    assert_correct_registration: UserAssertion,
) -> None:
    """Тест регистрации пользователя с невалидным email."""
    registration_data = registration_data_factory("test.com")
    response = client.post(reverse("registration"), data=registration_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db()
def test_authorization(
    client: Client,
    registration_data_factory: Callable[[], RegistrationData],
    assert_correct_registration: UserAssertion,
) -> None:
    """Тест успешной авторизации в сервисе."""
    registration_data = registration_data_factory()
    client.post(reverse("registration"), data=registration_data)
    response = client.post(reverse("auth"), data=registration_data)
    assert response.status_code == HTTPStatus.OK
    assert response.data["access"]
    assert response.data["refresh"]


@pytest.mark.django_db()
def test_unauthorization(
    client: Client,
    registration_data_factory: Callable[[], RegistrationData],
    assert_correct_registration: UserAssertion,
) -> None:
    """Тест неуспешной авторизации в сервисе."""
    registration_data = registration_data_factory()
    client.post(reverse("registration"), data=registration_data)
    response = client.post(
        reverse("auth"), data=registration_data_factory("anonymous@test.com")
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
