# rates-backend

Бэкенд сервиса для отслеживания динамики курса рубля по отношению к валютам на основе дневных котировок ЦБ РФ.

## Требования

* [Docker](https://docs.docker.com/)
* [docker-compose](https://docs.docker.com/compose/)

## Сборка и запуск

```bash
$ cd rates-backend
$ cp .env.example .env
$ docker network create rates-net
$ docker compose build
$ docker compose up
```

* API доступно на http://0.0.0.0:8888/api/v1/.
* Документация: http://0.0.0.0:8888/api/v1/docs/, http://0.0.0.0:8888/api/v1/redoc/.
* Запуск тестов:
```bash
$ docker-compose exec rates make tests
```