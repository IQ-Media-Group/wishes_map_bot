# Базовый образ
FROM python:3.11-slim


# Устанавливаем зависимости для работы с Poetry и компиляцией пакетов
RUN pip install poetry


# Создаём директорию для приложения
WORKDIR /app

# Копируем файлы проекта
COPY pyproject.toml poetry.lock /app/

# Устанавливаем зависимости
RUN poetry install --no-dev --no-interaction --no-ansi --no-root

# Копируем исходный код
COPY . /app/

# Команда для запуска бота
CMD ["poetry", "run", "python", "main.py"]