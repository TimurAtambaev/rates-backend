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
    assert_correct_user: UserAssertion,
) -> None:
    """Тест регистрации пользователей."""
    registration_data = registration_data_factory()
    response = client.post(reverse("registration"), data=registration_data)
    assert response.status_code == HTTPStatus.CREATED
    assert_correct_user(registration_data["email"], registration_data)
