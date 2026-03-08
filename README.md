# System B — Центральный реестр (ЦР)

Информационная система для межведомственного обмена документами и ведения реестра транзакций. Реализует логику приёма, хранения и выдачи юридически значимых сообщений (в эмулированном режиме криптографии).

## Live Demo

Проект развёрнут и доступен для тестирования:
**[Документация Swagger (система Б)](https://system-b-74d9.onrender.com/docs)**

> [!NOTE]
> Так как используется бесплатный тариф Render, при первом переходе по ссылке после долгого простоя может потребоваться **30-50 секунд** для «пробуждения» сервиса.

## Основные возможности

- **Приём входящих сообщений (`/api/messages/incoming`)**:
  - Полная валидация подписи конверта (`SignedApiData`).
  - Проверка целостности каждой транзакции (хэш и подпись).
  - Автоматическая генерация квитанций (сообщения типа 215) для подтверждения приёма.
- **Выдача исходящих сообщений (`/api/messages/outgoing`)**:
  - Поиск транзакций по временному диапазону (`SearchRequest`).
  - Поддержка пагинации (`limit`, `offset`).
- **Автоматическое сидирование (Seed Service)**:
  - При первом запуске (если БД пуста) создаются тестовые сообщения типов 201 (Выдача гарантии) и 202 (Принятие гарантии).
- **Эмуляция криптографии**:
  - Расчет хэшей SHA-256.
  - Эмуляция ЭЦП (Base64-кодирование хэша).
- **Слоеная архитектура**:
  - FastAPI (API), SQLAlchemy 2.0 Async (Storage), Pattern Unit of Work.

## Быстрый старт

### Требования
- Python 3.10+
- SQLite (используется aiosqlite для асинхронной работы)

### Установка

1. Клонируйте репозиторий.
2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Linux/macOS
   # или
   .\venv\Scripts\Activate.ps1 # Для Windows PowerShell
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Настройте переменные окружения в файле `.env` (см. `.env.example`).

### Запуск через Docker

Если у вас установлен Docker и Docker Compose, вы можете запустить проект одной командой:

```bash
docker-compose up --build
```

Приложение будет автоматически собрано и запущено на порту `8000`. База данных SQLite будет сохраняться в локальную директорию `./data` благодаря настроенным volumes.

Приложение будет доступно по адресу `http://localhost:8000`.
Интерактивная документация (Swagger): `http://localhost:8000/docs`.

## API Эндпоинты

### 1. Приём входящих сообщений
**POST** `/api/messages/incoming`

Пример запроса (`SignedApiData`):
```json
{
  "Data": "eyJUcmFuc2FjdGlvbnMiOlt7IlRyYW5zYWN0aW9uVHlwZSI6OSwiRGF0YSI6ImV5SkVZWFJoSWpvZ0ltVjVTa3BTUTBrMlNVTkplRWxwZDJkSmEyeDFXbTA0YVU5cFFXbFdSMVo2WkVOS09TSXNJQ0pUWlc1a1pYSkNjbUZ1WTJnaU9pQWlVMWxUVkVWTlgwRWlMQ0FpVW1WalpXbDJaWEpDY21GdVkyZ2lPaUFpVTFsVFZFVk5YMElpTENBaVNXNW1iMDFsYzNOaFoyVlVlWEJsSWpvZ01qQXhMQ0FpVFdWemMyRm5aVlJwYldVaU9pQWlNakF5TkMwd015MHdPRlF4TlRvd01Eb3dNQ0lzSUNKRGFHRnBia2QxYVdRaU9pQWlNVEV4TVRFeE1URXRNakl5TWkwek16TXpMVFEwTkRRdE5UVTFOVFUxTlRVMU5UVTFJaXdnSWxCeVpYWnBiM1Z6VkhKaGJuTmhZM1JwYjI1SVlYTm9Jam9nYm5Wc2JDd2dJazFsZEdGa1lYUmhJam9nYm5Wc2JIMD0iLCJTaWduZXJDZXJ0IjoiUTBWU1ZGOUIiLCJUcmFuc2FjdGlvblRpbWUiOiIyMDI0LTAzLTA4VDE1OjAwOjAwIiwiTWV0YWRhdGEiOm51bGwsIlRyYW5zYWN0aW9uSW4iOm51bGwsIlRyYW5zYWN0aW9uT3V0IjpudWxsLCJIYXNoIjoiOEQ0NUMxNjBFMEU2NEUxMUJDQTdBRTYyMDVBMkEwOEY1OTQ2RUVGOTYzMUNGQTVCODU1NUZGMEUzNzQxRjA1RiIsIlNpZ24iOiJPRVEwTlVNeE5qQkZNRVUyTkVVeE1VSkRRVGRCUlRZeU1EVkJNa0V3T0VZMU9UUTJSVVZHT1RZek1VTkdRVFZDT0RVMU5VWkdNRVV6TnpReFJqQTFSZz09In1dLCJDb3VudCI6MX0=",
  "Sign": "hqVtQeZ9ZKU+EUbHHSB3NEB3l6V9jEwah6lXLqb+1Fo=",
  "SignerCert": "Q0VSVF9B"
}
```

### 2. Запрос исходящих сообщений
**POST** `/api/messages/outgoing`

Пример запроса (`SignedApiData`):
```json
{
  "Data": "eyJTdGFydERhdGUiOiAiMjAyNC0wMy0wMVQwMDowMDowMCIsICJFbmREYXRlIjogIjIwMjQtMDMtMzFUMjM6NTk6NTkiLCAiTGltaXQiOiA1LCAiT2Zmc2V0IjogMH0=",
  "Sign": "92EWj+CDvL08E00VTFwanfRfA5vVNertf2DEMOpjyfk=",
  "SignerCert": "U1lTVEVNX0E="
}
```

## Тестирование

Проект покрыт автоматическими тестами (pytest).

```bash
pytest -v
```

Тесты включают:
- Валидацию криптографических функций.
- Интеграционные тесты API (incoming/outgoing).
- Проверку автоматической генерации квитанций (215).
- Тесты сидирования данных (идемпотентность и корректность заполнения).

## Стек технологий

- **Фреймворк**: FastAPI
- **База данных**: SQLite (через SQLAlchemy Async)
- **Валидация данных**: Pydantic v2
- **Тестирование**: Pytest + HTTPX

## Структура проекта

- `app/api/`: Роуты и обработчики запросов.
- `app/schemas/`: Pydantic-схемы (DTO).
- `app/services/`: Бизнес-логика (MessageService, ReceiptService, SeedService).
- `app/storage/`: Модели БД, репозитории и Unit of Work.
- `app/crypto/`: Эмуляция криптографических алгоритмов.
- `tests/`: Набор автоматических тестов.
