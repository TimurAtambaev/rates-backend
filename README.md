# rates-backend

Бекенд сервиса для отслеживания динамики курса рубля на основе дневных котировок ЦБ РФ.

## Требования

* [Docker](https://docs.docker.com/)
* [docker-compose](https://docs.docker.com/compose/)

## Сборка и запуск

```bash
$ cd rates-backend
$ cp .env.example .env
$ docker network create rates-net
$ docker-compose build
$ docker-compose up
```

API доступно на localhost:8888.