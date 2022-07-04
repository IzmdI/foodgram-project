![Foodgram](https://github.com/IzmdI/foodgram-project/actions/workflows/foodgram_workflow.yaml/badge.svg)

# Foodgram - «Продуктовый помощник»

«Продуктовый помощник» - это онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», фильтровать рецепты по времени приёма пищи, а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Как использовать

Вам понадобится [Docker](https://www.docker.com/). Просто склонируйте репозиторий и запустите docker-compose.

### Установка

Во-первых, откройте `.env.example`, задайте в нём переменные окружения и сохраните как `.env` без `.example`.
ВАЖНО: Установите свои секретный ключ для Django и пароль для доступа к базе данных!

```
SECRET_KEY="django_secret_key" # Придумайте свой
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=somepostgresuser
POSTGRES_PASSWORD=somepostgrespass # Придумайте свой
DB_HOST=db
DB_PORT=5432
```

Запустите сборку контейнеров:

```
docker-compose up
```

Foodgram будет развёрнут через Gunicorn с Базой Данных PostgreSQL на ващей локальной машине, номер порта 8000:

```
localhost:8000 %ИЛИ% 127.0.0.1:8000
```

Создайте администратора как в обычном Django-проекте. Лучше делать это внутри контейнера:

```
docker exec -it <CONTAINER ID> bash
```

```
python3 manage.py createsuperuser
```

Также для корректной работы необходимо выполнить миграции:

```
python3 manage.py migrate
```

Чтобы выйти из контейнера выполните команду `exit`:

```
exit
```

Отлично! Теперь можете управлять проектом из админки:

```
localhost:8000/admin
```

### Тестовые данные

Вы можете загрузить дамп с некоторыми данными, или создать их вручную через админку.
ВАЖНО: Загружать тестовые данные нужно внутри контейнера.

```
python3 manage.py shell  

>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.delete()
>>> quit()

python3 manage.py loaddata dump.json 
```

## Компоненты

* [Django 3.1](https://www.djangoproject.com/) - Фреймворк для веб-разработки на python
* [DRF 3.12](https://www.django-rest-framework.org/) - Фреймворк для реализации API в Django-проектах
* [PostgreSQL 13.2](https://www.postgresql.org/) - СУБД
* [Gunicorn 20.1](https://gunicorn.org/) - Python WSGI HTTP-Сервер
* [Docker 20](https://www.docker.com/) - Платформа для разработки, доставки и эксплуатации приложений

## Автор

* **[Andrew Smelov](https://github.com/IzmdI)**

## Лицензия

Проект использует MIT-лицензию, подробности в файле LICENSE.md
