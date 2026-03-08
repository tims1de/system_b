# Использование легковесного базового образа Python
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Установка системных зависимостей (если понадобятся в будущем)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Экспонируем порт FastAPI (8000)
EXPOSE 8000

# Команда запуска приложения
# --host 0.0.0.0 важен для доступа снаружи контейнера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
