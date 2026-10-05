# =============================================================================
# Dockerfile — WhatsApp-бот бронирования на FastAPI (Multi-stage)
# Docker Engine 29.x | Python 3.13 | Февраль 2026
#
# Контекст: Webhook-бот для WhatsApp Cloud API.
# Принимает сообщения и отправляет информацию о турах ОАЭ.
#
# Использование:
#   docker build -t whatsapp-bot .
#   docker run -d -p 8000:8000 --env-file .env whatsapp-bot
# =============================================================================

# --- Stage 1: Builder ---
FROM python:3.13-slim-bookworm AS builder

WORKDIR /app

# Отключаем .pyc и буферизацию
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Создаём virtualenv для чистого копирования
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копируем зависимости отдельно (кэширование слоёв)
COPY requirements.txt .

# Установка зависимостей
# ВНИМАНИЕ: --no-cache-dir для уменьшения размера, НЕ --no-deps!
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Production ---
FROM python:3.13-slim-bookworm

WORKDIR /app

# Создаём непривилегированного пользователя
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --ingroup app app

# Копируем virtualenv из builder
COPY --from=builder --chown=app:app /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Копируем исходный код
COPY --chown=app:app . .

# Переключаемся на непривилегированного пользователя
USER app

# Документируем порт (webhook принимает POST от Meta)
EXPOSE 8000

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Запуск через uvicorn (production)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
