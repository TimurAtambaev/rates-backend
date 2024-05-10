"""Конфигурация для тестов."""

pytest_plugins = [
    "tests.fixtures.registration",
    "tests.fixtures.rates",
    "tests.fixtures.analitics",
    "tests.fixtures.users",
]
