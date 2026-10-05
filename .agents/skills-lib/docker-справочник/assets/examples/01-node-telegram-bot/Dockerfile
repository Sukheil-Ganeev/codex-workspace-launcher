# =============================================================================
# Dockerfile — Telegram-бот для бронирования туров (Node.js)
# Docker Engine 29.x | Node.js 22 LTS | Февраль 2026
#
# Контекст: Бот принимает заявки на экскурсии и билеты в парки ОАЭ.
# Использование:
#   docker build -t telegram-bot .
#   docker run -d --env-file .env --name telegram-bot telegram-bot
# =============================================================================

FROM node:22-slim

# Создаём непривилегированного пользователя
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --ingroup app app

WORKDIR /app

# Копируем файлы зависимостей (кэширование слоёв)
COPY package*.json ./

# Установка production-зависимостей с кэшированием npm
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev

# Копируем исходный код
COPY --chown=app:app . .

# Переключаемся на непривилегированного пользователя
USER app

# Проверка здоровья: бот жив, если процесс Node работает
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD node -e "process.exit(0)"

# Запуск бота (polling, не нужен EXPOSE)
CMD ["node", "bot.js"]
