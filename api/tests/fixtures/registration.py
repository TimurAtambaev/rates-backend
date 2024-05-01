"""Фикстуры тестов регистрации и авторизации в сервисе."""
from typing import Protocol, TypedDict, Unpack

import pytest
from mimesis.locales import Locale
from mimesis.schema import Field, Schema


class RegistrationData(TypedDict, total=False):
    """Класс тестовых данных для регистрации нового пользователя."""

    email: str
    email: str
    first_name: str
    last_name: str
    password: str


class RegistrationDataFactory(Protocol):
    """Класс тестовых данных для регистрации."""

    def __call__(self, **fields: Unpack[RegistrationData]) -> RegistrationData:
        """Протокол фабрики тестовых данных нового пользователя."""


@pytest.fixture()
def registration_data_factory(faker_seed: int) -> RegistrationDataFactory:
    """Фабрика тестовых данных для регистрации."""

    def factory(**fields: Unpack[RegistrationData]) -> RegistrationData:
        mf = Field(locale=Locale.RU, seed=faker_seed)
        password = mf("password")  # by default passwords are equal
        schema = Schema(
            schema=lambda: {
                "email": mf("person.email"),
                "first_name": mf("person.first_name"),
                "last_name": mf("person.last_name"),
                "date_of_birth": mf("datetime.date"),
                "address": mf("address.city"),
                "job_title": mf("person.occupation"),
                "phone": mf("person.telephone"),
                "phone_type": mf("choice", items=[1, 2, 3]),
            }
        )
        return {
            **schema.create(iterations=1)[0],  # type: ignore[misc]
            **{"password1": password, "password2": password},
            **fields,
        }

    return factory  # type: ignore[misc]
