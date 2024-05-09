"""Фикстуры тестов регистрации и авторизации в сервисе."""
from typing import Callable, TypeAlias, TypedDict

import pytest
from mimesis import Person
from mimesis.schema import Field, Schema

from api.models import AppUser


class RegistrationData(TypedDict, total=False):
    """Класс тестовых данных для регистрации нового пользователя."""

    email: str
    first_name: str
    last_name: str
    password: str


@pytest.fixture()
def registration_data_factory() -> Callable[[], RegistrationData]:
    """Фабрика тестовых данных для регистрации."""

    def factory() -> RegistrationData:
        person = Person()
        return {
            "email": person.email(),
            "first_name": person.first_name(),
            "last_name": person.last_name(),
            "password": person.password(),
        }

    return factory


UserAssertion: TypeAlias = Callable[[str, RegistrationData], None]


@pytest.fixture(scope="session")
def assert_correct_user() -> UserAssertion:
    def factory(email: str, expected: RegistrationData) -> None:
        user = AppUser.objects.filter(email=email).first()
        assert user
        assert user.id
        assert user.is_active
        assert not user.is_superuser
        assert not user.is_staff

        expected.pop("password")  # пароль захеширован
        for field_name, data_value in expected.items():
            assert getattr(user, field_name) == data_value

    return factory
