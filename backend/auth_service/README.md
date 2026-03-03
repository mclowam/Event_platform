# Auth Service

Сервис аутентификации и управления пользователями. Отвечает за регистрацию, вход, выдачу и обновление JWT-токенов, а также предоставление информации о текущем пользователе.

## Стек

- Python 3.11, FastAPI, Uvicorn
- PostgreSQL 16 (asyncpg, SQLAlchemy 2.0)
- Alembic (миграции)
- python-jose (JWT), bcrypt (хеширование паролей)

## Запуск

```bash
docker-compose up auth-service

# Локально
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Порт: **8000**

## Переменные окружения

| Переменная   | Описание              | Пример       |
|--------------|-----------------------|--------------|
| DB_HOST      | Хост PostgreSQL       | postgres-auth |
| DB_PORT      | Порт PostgreSQL       | 5432         |
| DB_NAME      | Имя базы данных       | auth_db      |
| DB_USER      | Пользователь БД       | admin        |
| DB_PASSWORD  | Пароль БД             | admin        |
| PYTHONPATH   | Путь к модулям        | /main        |

Также в `core/config.py`:
- `SECRET_KEY` — ключ подписи JWT (по умолчанию захардкожен)
- `ALGORITHM` — алгоритм JWT (`HS256`)
- `ACCESS_EXPIRE_MIN` — время жизни access-токена (30 мин)
- `REFRESH_EXPIRE_DAYS` — время жизни refresh-токена (7 дней)

## Эндпоинты

### Публичные

| Метод | Путь              | Тело запроса            | Ответ          | Описание                    |
|-------|-------------------|-------------------------|----------------|-----------------------------|
| GET   | `/`               | —                       | `{"detail": "all ready!"}` | Проверка работоспособности |
| POST  | `/auth/register`  | `UserCreateSchema`      | 201            | Регистрация нового пользователя |
| POST  | `/auth/login`     | form: `username`, `password` | `TokenSchema` | Вход (OAuth2 form, username = email) |
| POST  | `/auth/refresh`   | `RefreshTokenSchema`    | `TokenSchema`  | Обновление пары токенов     |
| GET   | `/auth/user/email?email=...` | —            | `UserPayload`  | Получение пользователя по email |

### Требуют авторизации (Bearer)

| Метод | Путь        | Ответ        | Описание                 |
|-------|-------------|--------------|--------------------------|
| GET   | `/auth/me`  | `UserPayload`| Текущий пользователь     |

### Только для админа

| Метод | Путь             | Параметры            | Ответ                  | Описание               |
|-------|------------------|----------------------|------------------------|------------------------|
| GET   | `/admin/users`   | `page`, `size`       | Список пользователей   | Пагинированный список  |

## Схемы данных

### UserCreateSchema (запрос регистрации)

```
username:   str       — обязательно
email:      str       — обязательно
password:   str       — обязательно
first_name: str       — обязательно
last_name:  str       — обязательно
phone:      str|null  — необязательно
skills:     str|null  — необязательно
```

### TokenSchema (ответ логина/рефреша)

```
access_token:  str
refresh_token: str
token_type:    str  — "bearer"
```

### UserPayload (ответ /auth/me)

```
user_id: int
email:   str
role:    "volunteer" | "organizer" | "admin"
```

### UserReadSchema (расширенная информация)

```
id:         int
username:   str
email:      str
first_name: str|null
last_name:  str|null
role:       "volunteer" | "organizer" | "admin"
phone:      str|null
skills:     str|null
is_active:  bool
```

## Модель User (БД)

| Поле       | Тип          | Описание                    |
|------------|--------------|-----------------------------|
| id         | int (PK)     | Автоинкремент               |
| username   | str          | Имя пользователя            |
| email      | str (unique) | Email                       |
| password   | str          | Хеш пароля (bcrypt)         |
| first_name | str?         | Имя                         |
| last_name  | str?         | Фамилия                     |
| phone      | str?         | Телефон                     |
| skills     | str?         | Навыки                      |
| is_staff   | bool         | Служебный флаг (default false) |
| role       | str          | Роль (default "volunteer")  |
| is_active  | bool         | Активен (default true)      |

## Роли

- **volunteer** — волонтёр (по умолчанию при регистрации)
- **organizer** — организатор событий
- **admin** — администратор платформы

## Структура

```
auth_service/
├── main.py                 # FastAPI app, подключение роутеров
├── Dockerfile
├── requirements.txt
├── routers/
│   └── auth.py             # Эндпоинты /auth/*
├── services/
│   ├── __init__.py
│   ├── abstractions.py     # Протоколы (интерфейсы)
│   ├── auth_service.py     # Логика регистрации, логина, рефреша
│   ├── user_repository.py  # Работа с БД (User)
│   ├── token_service.py    # Создание и декодирование JWT
│   └── password_hashed.py  # Хеширование паролей (bcrypt)
├── schemas/
│   ├── roles.py            # UserRole enum, UserPayload
│   └── users.py            # UserCreateSchema, TokenSchema и др.
├── models/
│   └── user.py             # SQLAlchemy модель User
├── core/
│   ├── config.py           # Переменные окружения, SECRET_KEY
│   └── auth.py             # get_current_user (Bearer)
├── db/
│   ├── base.py             # Declarative Base
│   └── session.py          # AsyncSession
└── migrations/             # Alembic
```
