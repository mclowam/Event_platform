# Event Platform

Платформа для управления волонтёрскими мероприятиями. Организаторы создают события, волонтёры подают заявки, а посещаемость отслеживается через QR-коды.

## Архитектура

```
                    ┌──────────┐
                    │  Nginx   │ :80
                    │ Gateway  │
                    └────┬─────┘
         ┌───────────────┼───────────────┐────────────┐
         │               │               │            │
   ┌─────┴─────┐  ┌──────┴──────┐  ┌─────┴──────┐  ┌──┴───┐
   │   Auth    │  │   Events   │  │ Attendance │  │ Web  │
   │  Service  │  │  Service   │  │  Service   │  │ App  │
   │   :8000   │  │   :8001    │  │   :8002    │  │:5173 │
   └─────┬─────┘  └─────┬──┬───┘  └─────┬─────┘  └──────┘
         │               │  │            │
   ┌─────┴─────┐  ┌──────┴──┘──┐  ┌─────┴──────┐
   │ Postgres  │  │  Postgres  │  │  Postgres  │
   │  auth_db  │  │  event_db  │  │attendance_db│
   │   :5432   │  │   :5433    │  │   :5435    │
   └───────────┘  └─────┬──────┘  └────────────┘
                        │
                  ┌─────┴──────┐
                  │   MinIO    │
                  │  :9000/01  │
                  └────────────┘
```

Дополнительно: **RabbitMQ** (:5672, :15672) — подготовлен для notification_service.

## Сервисы

| Сервис               | Порт | Путь в gateway        | Описание                                    |
|----------------------|------|-----------------------|---------------------------------------------|
| **auth_service**     | 8000 | `/auth/`              | Регистрация, логин, JWT-токены, роли        |
| **events_service**   | 8001 | `/events`, `/applications` | События, изображения, заявки волонтёров |
| **attendance_service**| 8002| `/volunteers`, `/organizers` | QR-коды, check-in/out, часы, статистика |
| **notification_service** | — | —                    | Уведомления (в разработке)                  |
| **web-app (frontend)** | 5173 | `/` (всё остальное) | React SPA                                   |

Документация каждого сервиса — в `backend/<service>/README.md`.

## Роли пользователей

| Роль         | Возможности                                                    |
|--------------|----------------------------------------------------------------|
| **volunteer**| Просмотр событий, подача/отмена заявок, получение QR, просмотр часов |
| **organizer**| Всё выше + создание событий, сканирование QR, отметка по email, статистика |
| **admin**    | Всё выше + управление пользователями                           |

## Быстрый старт

### Требования

- Docker и Docker Compose
- Node.js 20+ (для локальной разработки фронта)

### Запуск всего проекта

```bash
docker-compose up --build
```

После запуска:
- **Фронтенд:** http://localhost (через gateway) или http://localhost:3000 (напрямую)
- **API Gateway:** http://localhost
- **MinIO Console:** http://localhost:9001
- **RabbitMQ Management:** http://localhost:15672 (guest/guest)

### Только бэкенд

```bash
docker-compose up auth-service event-service attendance-service gateway
```

### Только фронт (dev)

```bash
cd frontend/web
npm install
npm run dev
```

## Переменные окружения

Задаются в `docker-compose.yml` для каждого сервиса:

| Переменная       | Сервисы             | Описание                  |
|------------------|---------------------|---------------------------|
| DB_HOST          | auth, events, att.  | Хост PostgreSQL           |
| DB_PORT          | auth, events, att.  | Порт PostgreSQL           |
| DB_NAME          | auth, events, att.  | Имя базы данных           |
| DB_USER          | auth, events, att.  | Пользователь БД           |
| DB_PASSWORD      | auth, events, att.  | Пароль БД                 |
| MINIO_ENDPOINT   | events              | URL MinIO                 |
| MINIO_BUCKET     | events              | Бакет для изображений     |
| MINIO_ACCESS_KEY | events              | Ключ доступа MinIO        |
| MINIO_SECRET_KEY | events              | Секрет MinIO              |
| VITE_API_URL     | web-app             | Base URL API для фронта   |

## Аутентификация

- JWT Bearer-токены (access + refresh)
- Логин: `POST /auth/login` (OAuth2 form: `username` = email, `password`)
- Заголовок: `Authorization: Bearer <access_token>`
- Access-токен: 30 минут, Refresh-токен: 7 дней

## API — краткая справка

### Auth (`/auth`)

| Метод | Путь              | Auth  | Описание                    |
|-------|--------------------|-------|-----------------------------|
| POST  | `/auth/register`  | —     | Регистрация                 |
| POST  | `/auth/login`     | —     | Вход (form-urlencoded)      |
| POST  | `/auth/refresh`   | —     | Обновление токенов          |
| GET   | `/auth/me`        | Bearer| Текущий пользователь        |

### Events (`/events`)

| Метод | Путь                     | Auth             | Описание               |
|-------|--------------------------|------------------|------------------------|
| GET   | `/events`                | —                | Список событий         |
| GET   | `/events/{id}`           | —                | Детали события         |
| GET   | `/events/{id}/image`     | —                | Изображение события    |
| POST  | `/events`                | Organizer/Admin  | Создание события       |

### Applications (`/applications`)

| Метод  | Путь                      | Auth   | Описание          |
|--------|---------------------------|--------|--------------------|
| GET    | `/applications`           | Bearer | Мои заявки         |
| POST   | `/applications`           | Bearer | Подать заявку      |
| DELETE | `/applications/{event_id}`| Bearer | Отменить заявку    |

### Volunteers (`/volunteers`)

| Метод | Путь                        | Auth   | Описание                |
|-------|-----------------------------|--------|-------------------------|
| GET   | `/volunteers/qr/{event_id}` | Bearer | QR-код (PNG)            |
| GET   | `/volunteers/hours`         | Bearer | Мои суммарные часы      |

### Organizers (`/organizers`)

| Метод | Путь                           | Auth            | Описание                |
|-------|--------------------------------|-----------------|-------------------------|
| POST  | `/organizers/attendance/qr`    | Organizer/Admin | Отметка по QR-токену    |
| POST  | `/organizers/attendance/email` | Organizer/Admin | Отметка по email        |
| GET   | `/organizers/attendance/stats` | Organizer/Admin | Статистика по событию   |

## Структура проекта

```
Event_platform/
├── docker-compose.yml
├── nginx.conf
├── README.md                          # Этот файл
├── backend/
│   ├── auth_service/                  # Сервис аутентификации
│   │   └── README.md
│   ├── events_service/                # Сервис событий и заявок
│   │   └── README.md
│   ├── attendance_service/            # Сервис посещаемости
│   │   └── README.md
│   └── notification_service/          # Сервис уведомлений (заготовка)
│       └── README.md
└── frontend/
    └── web/                           # React SPA (Vite)
        └── FRONTEND_STRUCTURE.md
```
