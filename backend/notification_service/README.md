# Notification Service

Сервис уведомлений. На текущий момент находится в стадии заготовки — основная структура создана, но роутеры и бизнес-логика отсутствуют.

## Текущее состояние

- `main.py` — создан FastAPI app с CORS, импортирует роутеры, которых ещё нет (`routers.attendee`, `routers.event`)
- `requirements.txt` — зависимости определены
- Dockerfile — **отсутствует**
- В `docker-compose.yml` — **не подключён**
- В nginx — **не настроен**

Сервис **не запускается** в текущем виде из-за отсутствия модулей роутеров.

## Планируемый стек

- Python 3.11, FastAPI, Uvicorn
- RabbitMQ (aio-pika / aiormq) — получение событий из очередей
- Email-уведомления (fastapi-mail / aiosmtplib)

## Зависимости (requirements.txt)

```
aio-pika
aiormq
aiosmtplib
fastapi-mail
fastapi
uvicorn
```

## Планируемая функциональность

- Подписка на события через RabbitMQ (одобрение заявки, напоминание о событии, завершение смены)
- Отправка email-уведомлений волонтёрам и организаторам
- Возможно: WebSocket для push-уведомлений в реальном времени

## Что нужно для запуска

1. Создать `routers/attendee.py` и `routers/event.py` с нужными эндпоинтами или обработчиками очередей
2. Создать `Dockerfile`
3. Добавить сервис в `docker-compose.yml` с зависимостью от RabbitMQ
4. Добавить upstream и location в `nginx.conf` (если будут HTTP-эндпоинты)
