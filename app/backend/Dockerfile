# Базовый образ Python
FROM python:3.10-slim

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей в контейнер
COPY requirements.txt .

RUN pip install --upgrade pip
# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов приложения в контейнер
COPY . .

# Открытие порта для приложения
EXPOSE 8000

# Команда для запуска приложения через Uvicorn
CMD ["fastapi", "run", "server.py", "--port", "80"]



