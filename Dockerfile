FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION "~=1.6.1"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV TZ="UTC"

WORKDIR /app

RUN apt-get update && \
  apt-get install --no-install-recommends -y postgresql postgresql-contrib python-psycopg2 libpq-dev gcc musl-dev libc-dev libffi-dev libssl-dev cargo wget make wait-for-it curl git \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY . /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install

CMD bash -c "python manage.py migrate; python manage.py runserver 0.0.0.0:8888"
