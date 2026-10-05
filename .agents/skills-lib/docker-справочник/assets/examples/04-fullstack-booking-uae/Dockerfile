# =============================================================================
# Dockerfile — Booking API для туризма ОАЭ (Node.js 22)
# Docker Engine 29.x | Multi-stage | Февраль 2026
# =============================================================================

# --- Stage 1: Builder ---
FROM node:22-slim AS builder
WORKDIR /app

# Копируем файлы зависимостей
COPY package*.json ./

# Устанавливаем зависимости с кэшированием
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production

# --- Stage 2: Production ---
FROM node:22-slim AS production
WORKDIR /app

# Создаём непривилегированного пользователя
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --ingroup app app

# Копируем зависимости из builder
COPY --from=builder --chown=app:app /app/node_modules ./node_modules
COPY --from=builder --chown=app:app /app/package*.json ./

# Копируем исходный код
COPY --chown=app:app app.js ./

# Переключаемся на непривилегированного пользователя
USER app

EXPOSE 3000

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => r.statusCode === 200 ? process.exit(0) : process.exit(1))"

CMD ["node", "app.js"]
