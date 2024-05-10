"""Фикстуры создания пользователей."""
from typing import Any, Callable

import pytest
from django.test import Client
from django.urls import reverse
from django_fakery import factory

from api.models import AppUser


@pytest.fixture()
def user_token(
    client: Client,
) -> Callable[[Client, dict[str, Any]], tuple[AppUser, str]]:
    """Фабрика пользователей с авторизацией."""

    def _factory(**fields: dict) -> tuple[AppUser, str]:
        user = factory.make(AppUser, fields={"password": "test1234", **fields})
        response = client.post(
            reverse("auth"), data={"email": user.email, "password": "test1234"}
        )
        return user, response.data["access"]

    return _factory
