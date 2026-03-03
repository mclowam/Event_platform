# Attendance Service

Сервис учёта посещаемости волонтёров. Генерирует QR-коды для волонтёров, обрабатывает check-in/check-out (по QR или вручную по email) и считает отработанные часы.

## Стек

- Python 3.11, FastAPI, Uvicorn
- PostgreSQL 16 (asyncpg, SQLAlchemy 2.0)
- Alembic (миграции)
- python-jose (JWT для QR-токенов и проверки Bearer)
- qrcode + Pillow (генерация QR-изображений)
- httpx (HTTP-запросы к auth_service для поиска пользователя по email)

## Запуск

```bash
docker-compose up attendance-service

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

Порт: **8002**

## Переменные окружения

| Переменная   | Описание              | Пример              |
|--------------|-----------------------|----------------------|
| DB_HOST      | Хост PostgreSQL       | postgres-attendance  |
| DB_PORT      | Порт PostgreSQL       | 5432                 |
| DB_NAME      | Имя базы данных       | attendance_db        |
| DB_USER      | Пользователь БД       | admin                |
| DB_PASSWORD  | Пароль БД             | admin                |
| PYTHONPATH   | Путь к модулям        | /main                |

Также в `core/config.py`:
- `SECRET_KEY` — ключ подписи JWT и QR-токенов (`"SECRET_KEY"`)
- `ALGORITHM` — `HS256`

Межсервисное взаимодействие:
- `AUTH_SERVICE_URL` = `http://auth-service:8000/auth` (в `utils/users.py`) — для получения пользователя по email

## Эндпоинты

### Волонтёр (требуют авторизации)

| Метод | Путь                       | Ответ                        | Описание                        |
|-------|----------------------------|------------------------------|---------------------------------|
| GET   | `/volunteers/qr/{event_id}`| PNG (StreamingResponse)      | QR-код для отметки на событии   |
| GET   | `/volunteers/hours`        | `{"total_hours": float}`     | Суммарные волонтёрские часы     |

### Организатор / Админ (требуют роли organizer или admin)

| Метод | Путь                            | Тело запроса                      | Ответ           | Описание                     |
|-------|---------------------------------|-----------------------------------|-----------------|------------------------------|
| POST  | `/organizers/attendance/qr`     | `{"qr_token": str}`              | `ScanResponse`  | Check-in/out по QR-токену    |
| POST  | `/organizers/attendance/email`  | `{"email": str, "event_id": int}`| `ScanResponse`  | Ручная отметка по email      |
| GET   | `/organizers/attendance/stats`  | query: `event_id`                | `AttendanceStats`| Статистика по событию       |

## Схемы данных

### ScanResponse (ответ на check-in/out)

```
status:        str           — "success" | "warning"
message:       str           — описание результата
volunteer_id:  int           — ID волонтёра
event_id:      int           — ID события
current_state: AttendanceStatus — текущий статус
check_in_at:   datetime|null — время входа
check_out_at:  datetime|null — время выхода
hours_worked:  float         — отработанные часы (default 0.0)
```

### AttendanceStats (статистика по событию)

```
registered: int  — зарегистрированы, но не пришли
checked_in: int  — отметились на входе
completed:  int  — завершили смену
absent:     int  — отсутствуют
```

### ManualAttendanceRequest

```
email:    str  — email волонтёра
event_id: int  — ID события
```

## Модель Attendance (БД)

| Поле        | Тип               | Описание                       |
|-------------|--------------------|--------------------------------|
| id          | int (PK)           | Автоинкремент                  |
| user_id     | int (indexed)      | ID волонтёра                   |
| event_id    | int (indexed)      | ID события                     |
| status      | AttendanceStatus   | Статус (enum, default REGISTERED) |
| check_in_at | datetime?          | Время check-in                 |
| check_out_at| datetime?          | Время check-out                |
| hours_worked| float              | Часы (default 0.0)             |
| verified_by | int?               | Кто подтвердил (ID организатора) |
| created_at  | datetime           | Дата создания записи           |

### AttendanceStatus (enum)

- `REGISTERED` — зарегистрирован на событие
- `CHECKED_IN` — отметился на входе
- `COMPLETED` — завершил смену (check-out)
- `ABSENT` — отсутствует

## Логика QR-токенов

### Генерация (волонтёр)

1. Волонтёр запрашивает `GET /volunteers/qr/{event_id}`
2. Создаётся JWT-токен: `{sub: user_id, event_id, type: "attendance_qr", exp: +24h}`
3. Токен кодируется в QR-изображение (PNG) и возвращается как stream

### Сканирование (организатор)

1. Организатор сканирует QR → отправляет `POST /organizers/attendance/qr` с `qr_token`
2. Токен декодируется, проверяется `type == "attendance_qr"` и срок действия
3. По `user_id` + `event_id` определяется текущее состояние:

```
Нет записи        → создаётся запись со статусом CHECKED_IN
REGISTERED         → переводится в CHECKED_IN
CHECKED_IN (<60с)  → "Рано выходить" (отклонение)
CHECKED_IN (≥60с)  → переводится в COMPLETED, считаются hours_worked
COMPLETED          → "Смена уже закрыта" (предупреждение)
```

### Ручная отметка по email

Аналогичная логика, но `user_id` определяется через HTTP-запрос к auth_service:
`GET http://auth-service:8000/auth/user/email?email=...`

## Структура

```
attendance_service/
├── main.py                   # FastAPI app, подключение роутеров
├── Dockerfile
├── requirements.txt
├── routers/
│   ├── volunteer.py          # Эндпоинты /volunteers/*
│   └── organizer.py          # Эндпоинты /organizers/*
├── services/
│   ├── attendance.py         # Логика check-in/out по QR
│   ├── stats.py              # Подсчёт статистики
│   └── qr_service.py         # Генерация QR-изображений
├── schemas/
│   ├── attendance.py         # AttendanceStatus enum
│   ├── organizer.py          # ScanRequest, ScanResponse, ManualAttendanceRequest, AttendanceStats
│   └── user.py               # UserPayload
├── models/
│   └── attendance.py         # SQLAlchemy модель Attendance
├── utils/
│   ├── tokens.py             # Создание и декодирование QR JWT-токенов
│   └── users.py              # HTTP-запрос к auth_service (поиск по email)
├── core/
│   ├── config.py             # Переменные окружения, SECRET_KEY
│   ├── auth.py               # get_current_user (Bearer)
│   └── permissions.py        # is_organizer_or_admin
├── db/
│   ├── base.py               # Declarative Base
│   └── session.py            # AsyncSession
└── migrations/               # Alembic
```
