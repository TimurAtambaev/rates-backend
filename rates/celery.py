"""Модуль с настройками celery."""
from celery import Celery

from rates import settings

app = Celery(
    "rates",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
)


if __name__ == "__main__":
    app.start()
