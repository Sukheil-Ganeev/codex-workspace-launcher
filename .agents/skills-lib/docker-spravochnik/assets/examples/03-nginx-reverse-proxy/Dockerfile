# =============================================================================
# Dockerfile — Nginx reverse proxy для микросервисов туризма ОАЭ
# Docker Engine 29.x | Nginx 1.27 Alpine | Февраль 2026
#
# Проксирует запросы к backend-сервисам (боты, API бронирования).
#
# Использование:
#   docker build -t nginx-proxy .
#   docker run -d -p 80:80 --name proxy nginx-proxy
# =============================================================================

FROM nginx:1.27-alpine

# Удаляем дефолтную конфигурацию
RUN rm /etc/nginx/conf.d/default.conf

# Копируем кастомную конфигурацию
COPY nginx.conf /etc/nginx/nginx.conf

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/health || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
