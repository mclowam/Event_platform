# Events Service

Сервис управления событиями и заявками волонтёров. Отвечает за создание, получение и отображение мероприятий, а также за подачу и отмену заявок на участие.

## Стек

- Python 3.11, FastAPI, Uvicorn
- PostgreSQL 16 (asyncpg, SQLAlchemy 2.0)
- Alembic (миграции)
- MinIO (S3-совместимое хранилище изображений, через aioboto3)
- python-jose (проверка JWT)

## Запуск

```bash
docker-compose up event-service

# Локально
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Порт: **8001**

## Переменные окружения

| Переменная       | Описание                  | Пример              |
|------------------|---------------------------|----------------------|
| DB_HOST          | Хост PostgreSQL           | postgres-event       |
| DB_PORT          | Порт PostgreSQL           | 5432                 |
| DB_NAME          | Имя базы данных           | event_db             |
| DB_USER          | Пользователь БД           | admin                |
| DB_PASSWORD      | Пароль БД                 | admin                |
| MINIO_ENDPOINT   | URL MinIO                 | http://minio:9000    |
| MINIO_BUCKET     | Имя бакета                | events-photos        |
| MINIO_ACCESS_KEY | Ключ доступа MinIO        | admin                |
| MINIO_SECRET_KEY | Секрет MinIO              | password123          |
| PYTHONPATH       | Путь к модулям            | /main                |

Также в `core/config.py`:
- `SECRET_KEY` — ключ проверки JWT (`"SECRET_KEY"`)
- `ALGORITHM` — `HS256`

## Эндпоинты

### События (публичные)

| Метод | Путь                     | Параметры           | Ответ                       | Описание                     |
|-------|--------------------------|---------------------|-----------------------------|------------------------------|
| GET   | `/events`                | `page=1`, `size=2`  | `list[EventResponseSchema]` | Список событий (пагинация)   |
| GET   | `/events/{event_id}`     | —                   | `EventResponseSchema`       | Детали события               |
| GET   | `/events/{event_id}/image` | —                 | `StreamingResponse` (image) | Изображение события из MinIO |

### Создание события (organizer / admin)

| Метод | Путь      | Тело (multipart/form-data)                                                     | Ответ                 |
|-------|-----------|--------------------------------------------------------------------------------|-----------------------|
| POST  | `/events` | `title`, `description`, `location`, `status_id`, `max_volunteers`, `start_time`, `end_time`, `file` (image) | `EventResponseSchema` |

### Заявки (требуют авторизации)

| Метод  | Путь                      | Тело                         | Ответ                             | Описание             |
|--------|---------------------------|------------------------------|------------------------------------|----------------------|
| GET    | `/applications`           | —                            | `list[ApplicationResponseSchema]` | Мои заявки           |
| POST   | `/applications`           | `{"event_id": int}`          | `ApplicationResponseSchema`        | Подать заявку        |
| DELETE | `/applications/{event_id}`| —                            | 204 No Content                     | Отменить заявку      |

## Схемы данных

### EventResponseSchema

```
id:              int
title:           str
description:     str
location:        str
max_volunteers:  int
start_time:      datetime
end_time:        datetime
organizer_id:    int
status:          { id: int, name: str }
image_url:       str|null
created_at:      datetime
updated_at:      datetime
```

### ApplicationResponseSchema

```
id:         int
user_id:    int
event_id:   int
applied_at: datetime
event:      EventResponseSchema
```

## Модели (БД)

### Event

| Поле           | Тип              | Описание                     |
|----------------|------------------|------------------------------|
| id             | int (PK)         | Автоинкремент                |
| title          | str              | Название события             |
| description    | str              | Описание                     |
| organizer_id   | int              | ID организатора (из JWT)     |
| location       | str              | Место проведения             |
| max_volunteers | int              | Максимум волонтёров          |
| status_id      | int (FK)         | Ссылка на Status             |
| image_url      | str?             | Путь к изображению в MinIO   |
| start_time     | datetime (tz)    | Начало                       |
| end_time       | datetime (tz)    | Конец                        |
| created_at     | datetime (tz)    | Дата создания                |
| updated_at     | datetime (tz)    | Дата обновления              |

### VolunteerApplication

| Поле       | Тип           | Описание                                    |
|------------|---------------|---------------------------------------------|
| id         | int (PK)      | Автоинкремент                               |
| event_id   | int (FK)      | Ссылка на Event (cascade delete)            |
| user_id    | int           | ID волонтёра (из JWT)                       |
| applied_at | datetime (tz) | Дата подачи заявки                          |

Уникальное ограничение: `(event_id, user_id)` — один пользователь = одна заявка на событие.

### Status

| Поле | Тип      | Описание          |
|------|----------|--------------------|
| id   | int (PK) | Автоинкремент      |
| name | str      | Название статуса   |

## Хранение изображений

Изображения событий загружаются в MinIO (S3-совместимое хранилище):
- Бакет: `events-photos`
- При создании события файл загружается через `aioboto3`
- При запросе `/events/{id}/image` файл стримится из MinIO через `StreamingResponse`

## Структура

```
events_service/
├── main.py                   # FastAPI app, подключение роутеров
├── Dockerfile
├── requirements.txt
├── routers/
│   ├── event.py              # Эндпоинты /events/*
│   └── attendee.py           # Эндпоинты /applications/*
├── services/
│   ├── __init__.py
│   ├── abstractions.py       # Протоколы (интерфейсы)
│   ├── event_service.py      # Бизнес-логика событий
│   ├── event_repository.py   # Работа с БД (Event)
│   ├── application_service.py # Бизнес-логика заявок
│   ├── application_repository.py # Работа с БД (Application)
│   └── image_storage.py      # MinIO (загрузка/получение файлов)
├── schemas/
│   ├── event.py              # EventResponseSchema, EventCreateSchema
│   ├── attendee.py           # ApplicationResponseSchema и др.
│   └── user.py               # UserPayload (из JWT)
├── models/
│   ├── __init__.py
│   ├── event.py              # SQLAlchemy модель Event
│   ├── attendee.py           # SQLAlchemy модель VolunteerApplication
│   └── status.py             # SQLAlchemy модель Status
├── core/
│   ├── config.py             # Переменные окружения, SECRET_KEY
│   ├── auth.py               # get_current_user (Bearer)
│   ├── permissions.py        # is_organizer_or_admin
│   └── minio_client.py       # Конфигурация MinIO (aioboto3)
├── db/
│   ├── base.py               # Declarative Base
│   └── session.py            # AsyncSession
└── migrations/               # Alembic
```
