FROM python:3.11-slim-buster

RUN apt-get update && \
  apt-get install --no-install-recommends -y postgresql postgresql-contrib  \
    python-psycopg2 libpq-dev gcc musl-dev libc-dev libffi-dev libssl-dev  \
    cargo wget make wait-for-it curl git \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY poetry.lock pyproject.toml ./

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:$PYTHONPATH
ENV POETRY_VERSION "~=1.7.1"
ENV TZ="Europe/Moscow"

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY . /app/
