# Docker Cheatsheet -- Шпаргалка

> Все команды Docker CLI, Compose CLI и Dockerfile инструкции
> Docker Engine 29.x | Compose v2.40+ (CLI v5.x) | Февраль 2026

---

## Docker CLI -- Контейнеры

| Команда | Описание |
|---------|----------|
| `docker run -d --name web -p 8080:80 nginx` | Запустить контейнер в фоне |
| `docker run -it --rm ubuntu bash` | Интерактивный shell, автоудаление |
| `docker run --env-file .env myapp` | Запуск с переменными из файла |
| `docker run -v $(pwd)/src:/app/src myapp` | Bind mount для разработки |
| `docker run -v pgdata:/var/lib/postgresql/data postgres` | Named volume |
| `docker run --memory 512m --cpus 1.5 myapp` | С лимитами ресурсов |
| `docker run --restart unless-stopped myapp` | С автоперезапуском |
| `docker run --network backend myapp` | В конкретной сети |
| `docker run --read-only --tmpfs /tmp myapp` | Read-only FS |
| `docker ps` | Запущенные контейнеры |
| `docker ps -a` | Все контейнеры (включая остановленные) |
| `docker stop <container>` | Graceful stop (SIGTERM, 10s, SIGKILL) |
| `docker stop -t 30 <container>` | Stop с кастомным таймаутом |
| `docker kill <container>` | Немедленное убийство (SIGKILL) |
| `docker rm <container>` | Удалить остановленный |
| `docker rm -f <container>` | Принудительно удалить (даже работающий) |
| `docker restart <container>` | Перезапуск |
| `docker exec -it <container> bash` | Shell внутри контейнера |
| `docker exec <container> cat /etc/hosts` | Выполнить одну команду |
| `docker logs -f <container>` | Логи в реальном времени |
| `docker logs --tail 100 <container>` | Последние 100 строк |
| `docker logs --since 5m <container>` | За последние 5 минут |
| `docker stats` | Потребление ресурсов (все контейнеры) |
| `docker top <container>` | Процессы внутри |
| `docker inspect <container>` | Полная информация (JSON) |
| `docker port <container>` | Проброшенные порты |
| `docker cp <c>:/app/log.txt ./log.txt` | Копирование из контейнера |
| `docker cp ./data.json <c>:/app/data.json` | Копирование в контейнер |
| `docker diff <container>` | Изменения файловой системы |
| `docker wait <container>` | Ожидать завершения (возвращает exit code) |
| `docker attach <container>` | Подключиться к PID 1 (Ctrl+P,Q для detach) |
| `docker debug <container>` | Shell с инструментами (даже distroless) |
| `docker container prune` | Удалить все остановленные |

---

## Docker CLI -- Образы

| Команда | Описание |
|---------|----------|
| `docker pull nginx:1.27-alpine` | Скачать образ |
| `docker pull ghcr.io/org/app:v1.0` | Из GHCR |
| `docker build -t myapp:v1.0 .` | Собрать из Dockerfile |
| `docker build -f Dockerfile.prod -t myapp:prod .` | Из конкретного Dockerfile |
| `docker build --target builder .` | Собрать конкретный stage |
| `docker build --secret id=key,src=./key.txt .` | С build-time секретом |
| `docker tag myapp:latest ghcr.io/org/app:v1.0` | Присвоить тег |
| `docker push ghcr.io/org/app:v1.0` | Push в реестр |
| `docker images` / `docker image ls` | Список локальных образов |
| `docker image history <image>` | Слои и команды |
| `docker image inspect <image>` | Полная информация |
| `docker manifest inspect <image>` | Платформы и digest |
| `docker rmi <image>` / `docker image rm <image>` | Удалить образ |
| `docker image prune` | Удалить dangling (без тега) |
| `docker image prune -a` | Удалить все неиспользуемые |
| `docker search <name>` | Поиск на Docker Hub |

---

## Docker CLI -- Volumes

| Команда | Описание |
|---------|----------|
| `docker volume create mydata` | Создать named volume |
| `docker volume ls` | Список |
| `docker volume ls --filter dangling=true` | Неиспользуемые |
| `docker volume inspect mydata` | Информация |
| `docker volume rm mydata` | Удалить |
| `docker volume prune` | Удалить все неиспользуемые |

---

## Docker CLI -- Сети

| Команда | Описание |
|---------|----------|
| `docker network create mynet` | Создать bridge сеть |
| `docker network create --subnet 172.20.0.0/16 mynet` | С конкретной подсетью |
| `docker network ls` | Список сетей |
| `docker network inspect mynet` | Подробности (контейнеры, subnet) |
| `docker network connect mynet <container>` | Подключить контейнер |
| `docker network disconnect mynet <container>` | Отключить |
| `docker network rm mynet` | Удалить |
| `docker network prune` | Удалить неиспользуемые |

---

## Docker CLI -- Система

| Команда | Описание |
|---------|----------|
| `docker version` | Версия клиента и сервера |
| `docker info` | Подробная информация о системе |
| `docker system df` | Использование диска |
| `docker system df -v` | Детально |
| `docker system prune` | Очистка (контейнеры, сети, dangling, cache) |
| `docker system prune -a` | + все образы без контейнеров |
| `docker system prune -a --volumes` | + volumes (ОСТОРОЖНО!) |
| `docker builder prune` | Очистка build cache |
| `docker builder prune --filter "until=168h"` | Cache старше 7 дней |
| `docker events` | События daemon в реальном времени |
| `docker login` | Авторизация (Docker Hub) |
| `docker login ghcr.io` | Авторизация (GHCR) |
| `docker logout` | Выход |

### Генерация проекта

| Команда | Описание |
|---------|----------|
| `docker init` | Интерактивный генератор Dockerfile + compose.yaml + .dockerignore |

---

## Docker CLI -- Multi-platform (Buildx)

| Команда | Описание |
|---------|----------|
| `docker buildx create --name mybuilder --use` | Создать builder |
| `docker buildx ls` | Список builders |
| `docker buildx build --platform linux/amd64,linux/arm64 -t img --push .` | Кросс-сборка |
| `docker buildx build --load -t img .` | Сборка + загрузить локально |
| `docker buildx inspect` | Информация о builder |
| `docker buildx rm mybuilder` | Удалить builder |
| `docker buildx bake` | Сборка по HCL-конфигурации (docker-bake.hcl) |
| `docker buildx bake --print` | Показать план сборки без выполнения |

---

## Docker CLI -- Scout

| Команда | Описание |
|---------|----------|
| `docker scout quickview <image>` | Обзор уязвимостей |
| `docker scout cves <image>` | Список CVE |
| `docker scout cves --epss <image>` | CVE с вероятностью эксплуатации |
| `docker scout sbom <image>` | Генерация SBOM |
| `docker scout recommendations <image>` | Рекомендации обновления |

---

## Docker Compose CLI

| Команда | Описание |
|---------|----------|
| `docker compose up` | Запуск на переднем плане |
| `docker compose up -d` | Запуск в фоне |
| `docker compose up -d --build` | Пересобрать + запустить |
| `docker compose up -d --wait` | Ждать healthcheck |
| `docker compose up -d --scale api=3` | Масштабирование |
| `docker compose down` | Остановить + удалить контейнеры/сети |
| `docker compose down -v` | + удалить volumes |
| `docker compose down --rmi all` | + удалить образы |
| `docker compose ps` | Статус сервисов |
| `docker compose logs -f api` | Логи сервиса (follow) |
| `docker compose logs --tail 50` | Последние 50 строк |
| `docker compose exec api bash` | Shell в контейнере |
| `docker compose exec db psql -U postgres` | Команда в контейнере |
| `docker compose build` | Собрать все образы |
| `docker compose build --no-cache` | Без кэша |
| `docker compose pull` | Скачать все образы |
| `docker compose push` | Запушить собранные |
| `docker compose watch` | Hot-reload (Compose Watch) |
| `docker compose --profile dev up` | Активировать профиль |
| `docker compose config` | Валидация compose-файла |
| `docker compose cp` | Копировать файлы между хостом и контейнером |
| `docker compose alpha dry-run` | Показать что будет запущено (без запуска) |
| `docker compose version` | Версия Compose |

---

## Dockerfile -- Инструкции

| Инструкция | Описание | Пример |
|------------|----------|--------|
| `FROM` | Базовый образ (новый stage) | `FROM python:3.13-slim AS builder` |
| `RUN` | Выполнить команду (новый слой) | `RUN apt-get update && apt-get install -y curl` |
| `COPY` | Копировать файлы из context | `COPY requirements.txt .` |
| `COPY --from=` | Копировать из другого stage | `COPY --from=builder /app/dist ./dist` |
| `COPY --link` | Независимый слой (BuildKit) | `COPY --link --from=builder /app .` |
| `COPY --chown=` | С указанием владельца | `COPY --chown=app:app . /app` |
| `ADD` | Как COPY + распаковка архивов | `ADD app.tar.gz /app/` **(предпочитай COPY)** |
| `WORKDIR` | Рабочая директория | `WORKDIR /app` |
| `ENV` | Переменная окружения (в образе) | `ENV PYTHONUNBUFFERED=1` |
| `ARG` | Переменная сборки (НЕ в контейнере) | `ARG VERSION=1.0` |
| `EXPOSE` | Документировать порт | `EXPOSE 8000` |
| `CMD` | Команда по умолчанию (переопределяется) | `CMD ["uvicorn", "app:app"]` |
| `ENTRYPOINT` | Основной процесс (не переопределяется) | `ENTRYPOINT ["python", "-m"]` |
| `USER` | Пользователь (безопасность) | `USER appuser` |
| `HEALTHCHECK` | Проверка здоровья | `HEALTHCHECK CMD curl -f localhost/health` |
| `VOLUME` | Точка монтирования | `VOLUME ["/data"]` |
| `LABEL` | Метаданные | `LABEL version="1.0"` |
| `SHELL` | Shell по умолчанию | `SHELL ["/bin/bash", "-c"]` |
| `STOPSIGNAL` | Сигнал остановки | `STOPSIGNAL SIGQUIT` |

---

## Dockerfile -- BuildKit RUN --mount

| Тип | Синтаксис | Назначение |
|-----|-----------|-----------|
| **cache** | `RUN --mount=type=cache,target=/root/.cache/pip pip install -r req.txt` | Персистентный кэш между сборками |
| **secret** | `RUN --mount=type=secret,id=key cat /run/secrets/key` | Секрет (не в слоях!) |
| **ssh** | `RUN --mount=type=ssh git clone git@github.com:org/repo.git` | SSH forwarding |
| **bind** | `RUN --mount=type=bind,source=.,target=/src ls /src` | Временный bind mount |

---

## compose.yaml -- Структура

```yaml
services:          # Контейнеры (обязательный)
  app:
    image: myapp   # или build: ./path
    ports: ["8080:80"]
    volumes: [data:/app/data]
    environment:
      KEY: value
    env_file: .env
    depends_on:
      db: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    restart: unless-stopped
    deploy:
      resources:
        limits: { cpus: '1.0', memory: 512M }
    profiles: [dev]
    secrets: [db_password]
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src

networks:          # Сети
  backend:
    driver: bridge
    internal: true

volumes:           # Тома
  data:
    driver: local

include:                          # Импорт других compose-файлов (v2.20+)
  - compose.db.yaml
  - compose.monitoring.yaml

secrets:           # Секреты
  db_password:
    file: ./secrets/db_pw.txt

configs:           # Конфигурации
  nginx-conf:
    file: ./nginx.conf
```

---

## .dockerignore -- Шаблон

```dockerignore
.git
.gitignore
.env
*.env
.env.*
node_modules
__pycache__
*.pyc
.venv
venv
dist
build
*.md
!README.md
Dockerfile*
compose*.yml
compose*.yaml
.dockerignore
.vscode
.idea
*.log
*.tmp
.DS_Store
Thumbs.db
coverage
.nyc_output
tests
*.pem
*.key
```

---

## Restart Policies

| Политика | Crash | Daemon restart | После docker stop |
|----------|:-----:|:--------------:|:-----------------:|
| `no` | -- | -- | -- |
| `on-failure:N` | да | -- | -- |
| `always` | да | да | да (!) |
| `unless-stopped` | да | нет (если был остановлен) | -- |

---

## Port Mapping

```bash
-p 8080:80             # host:container
-p 127.0.0.1:8080:80  # только localhost
-p 80                  # random host port
-p 8000-8005:8000-8005 # диапазон
-P                     # все EXPOSE порты (random)
-p 5353:53/udp         # UDP
```

---

## Resource Limits

```bash
--memory 512m           # жёсткий лимит RAM
--memory-reservation 256m  # мягкий лимит
--cpus 1.5              # ядра CPU
--cpu-shares 512        # относительный вес
--cpuset-cpus "0,2"     # привязка к ядрам
--pids-limit 256        # лимит процессов
--read-only             # read-only filesystem
--tmpfs /tmp            # writable tmpfs
```

---

## Полезные фильтры inspect

```bash
# IP-адрес
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <c>

# Exit code
docker inspect -f '{{.State.ExitCode}}' <c>

# OOM killed
docker inspect -f '{{.State.OOMKilled}}' <c>

# Restart count
docker inspect -f '{{.RestartCount}}' <c>

# Mounts
docker inspect -f '{{json .Mounts}}' <c> | jq
```
