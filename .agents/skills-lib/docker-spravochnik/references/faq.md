# Docker FAQ -- Часто задаваемые вопросы

> 29 вопросов-ответов по Docker (февраль 2026)

---

### Q1: Docker Desktop платный?

**A:** Docker Desktop бесплатен (Personal план) для: персонального использования, open source, компаний < 250 человек И < $10M дохода. Компании >= 250 человек ИЛИ >= $10M обязаны купить подписку (Pro $9/мес, Team $15/юзер/мес, Business $24/юзер/мес -- annual billing, с декабря 2024). **Docker Engine** полностью бесплатный (Apache 2.0) без ограничений.

---

### Q2: Docker Desktop vs Docker Engine -- что выбрать?

**A:** Docker Desktop (Windows/macOS) -- для локальной разработки: GUI, встроенный K8s, Scout, Model Runner. Docker Engine (Linux) -- для серверов и CI/CD: нативная производительность, без GUI-оверхеда, бесплатная лицензия. На Linux-десктопе можно использовать оба.

---

### Q3: Какая версия Docker Engine актуальна?

**A:** Docker Engine 29.x (февраль 2026). Ключевые изменения: containerd image store дефолтный, cgroup v1 deprecated, nftables (экспериментально), DCT удален из CLI, минимальная API 1.44. Docker Desktop текущая версия -- 4.60.

---

### Q4: Docker Compose v1 или v2?

**A:** Только v2. Compose v1 (`docker-compose`, Python-бинарник) мёртв с июня 2023. v2 -- плагин Docker CLI (`docker compose`, без дефиса), написан на Go, быстрее в 2-3x. CLI перешёл на нумерацию v5.x (пропущены v3/v4, чтобы не путать с форматами compose-файлов). Замени `docker-compose` на `docker compose` во всех скриптах.

---

### Q5: Нужно ли поле `version` в compose.yml?

**A:** Нет. Compose v2 его игнорирует и выдает предупреждение. Удали. Рекомендуемое имя файла: `compose.yaml` (каноническое) или `compose.yml`.

---

### Q6: Какой base image выбрать для Python?

**A:** `python:3.13-slim-bookworm`. Не Alpine (musl libc ломает C-extensions, DNS проблемы). Не `python:latest` (непредсказуемо). Для максимальной безопасности: multi-stage с distroless. Для modern Python: uv вместо pip.

---

### Q7: Alpine или Debian-slim?

**A:** Debian-slim для большинства случаев. Alpine (musl libc) вызывает проблемы с Python C-extensions (numpy, pandas, psycopg2), DNS-резолвинг иногда ведёт себя иначе. Alpine подходит для простых Go/Rust бинарников и сервисов без native-зависимостей. Размер Alpine ~5 MB vs slim ~80 MB -- разница несущественна для production.

---

### Q8: Как хранить секреты в Docker?

**A:** **Никогда** через ENV или ARG в Dockerfile (видны в `docker history`). Используй:
- Build-time: `RUN --mount=type=secret,id=key`
- Runtime (Compose): секция `secrets:` (файлы в `/run/secrets/`)
- Production: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault

---

### Q9: Что такое multi-stage build?

**A:** Несколько `FROM` в одном Dockerfile. Каждый FROM начинает новый stage. Инструменты сборки (компиляторы, dev-зависимости) остаются в builder stage, не попадают в prod-образ. Уменьшает размер на 50-90%. BuildKit собирает только нужные stages.

---

### Q10: Как ускорить сборку Docker?

**A:** 1) Порядок слоёв: от редко к часто меняющимся. 2) Кэш зависимостей отдельно от кода (`COPY requirements.txt .` перед `COPY . .`). 3) BuildKit cache mounts (`--mount=type=cache`). 4) .dockerignore. 5) В CI: `cache-from: type=gha` (GitHub Actions) или registry cache.

---

### Q11: Named volume vs bind mount?

**A:** Named volume -- управляется Docker, подходит для данных БД, uploads, production. Bind mount -- маппинг пути хоста, для разработки (hot-reload кода). На macOS/Windows named volumes значительно быстрее bind mounts (данные внутри VM).

---

### Q12: Как бэкапить Docker volumes?

**A:** Для БД: `docker exec my_postgres pg_dump -U postgres mydb > backup.sql` (логический дамп, без остановки). Для файлов: `docker run --rm -v mydata:/data:ro -v $(pwd):/backup alpine tar czf /backup/data.tar.gz -C /data .`. Физический tar работающей БД может привести к коррупции -- всегда предпочитай логический дамп.

---

### Q13: Docker Swarm или Kubernetes?

**A:** Для 1-3 VPS и простых сервисов -- Docker Compose достаточно. Swarm -- для быстрого HA на 3-10 узлах без изучения K8s. Kubernetes -- для 10+ сервисов, auto-scaling, canary/blue-green деплоев, multi-cloud. 96%+ организаций используют K8s, но Compose/Swarm растёт среди разработчиков (PHP 17% -> 24%).

---

### Q14: Что такое Docker Model Runner?

**A:** Локальный запуск LLM через Docker. Совместим с OpenAI API. Поддержка Apple Silicon, NVIDIA GPU, Vulkan (любой GPU). GA-статус. Интеграция с Compose: `provider.type: model`. Позволяет запускать модели (Llama, Mistral и др.) локально без внешних сервисов.

---

### Q15: Что такое Docker MCP Toolkit?

**A:** Интерфейс управления контейнеризированными MCP-серверами в Docker Desktop. MCP Catalog на Docker Hub -- 100+ готовых серверов. MCP Gateway -- безопасный шлюз. Поддержка Claude, Cursor. Все образы mcp/ подписаны Docker и включают SBOM.

---

### Q16: Docker Scout -- что это и бесплатно ли?

**A:** Встроенный инструмент анализа безопасности: SBOM, CVE, EPSS scoring (вероятность эксплуатации). Free tier: до 3 репозиториев с real-time мониторингом. Альтернативы: Trivy (open source, универсальный), Grype (лёгкий для CI).

---

### Q17: Подходит ли Docker для production?

**A:** Да, с соблюдением best practices: rootless mode, non-root user, resource limits, HEALTHCHECK, log rotation, Docker Scout/Trivy для сканирования, secrets management. Docker Compose на VPS подходит для малых и средних проектов. Для масштабирования -- Kubernetes.

---

### Q18: Podman -- замена Docker?

**A:** Podman -- daemonless, rootless by design альтернатива. CLI совместим с Docker (`alias docker=podman`). Лучше для CI/CD (нет DinD хаков). Но экосистема Docker шире (Desktop, Scout, Build Cloud, Model Runner). Для production Linux-серверов Podman -- отличный выбор. Docker Desktop необходим на macOS/Windows.

---

### Q19: Как деплоить через Docker на VPS?

**A:** GitHub Actions -> Build -> Push GHCR -> SSH -> `docker compose pull && docker compose up -d`. Для малых проектов -- самая простая и надёжная схема. Для ARM (Oracle Cloud) -- `platforms: linux/arm64` в build-push-action. Альтернатива для CI: **Docker Build Cloud** -- облачные builders с нативной поддержкой linux/amd64 и linux/arm64 (без QEMU). Очистка после деплоя: `docker image prune -f`.

---

### Q20: Oracle Cloud Free Tier для Docker -- что доступно?

**A:** До 4 OCPU + 24 GB RAM ARM Ampere A1, бесплатно навсегда. Архитектура `linux/arm64`. Все основные образы (Python, Node, Nginx, Postgres) поддерживают ARM. Нет GPU -- для AI/ML используй cloud API (Groq, OpenAI). Установка Docker стандартная.

---

### Q21: Docker Content Trust ещё работает?

**A:** Нет. DCT удален из CLI в Engine v29. Может быть собран как отдельный плагин. Замены: **Sigstore cosign** (keyless signing, рекомендуется) или **Notation** (OCI-совместимые подписи, CNCF). Если `DOCKER_CONTENT_TRUST=1` в окружении -- отключи.

---

### Q22: Watchtower для автообновления контейнеров?

**A:** Watchtower **официально заархивирован** (декабрь 2025), несовместим с Docker 28+/29+ (устаревший API). Альтернативы: **What's Up Docker (WUD)** -- мониторинг + обновление + dashboard, **DIUN** -- только нотификации. Для production лучше CI/CD deploy через GitHub Actions.

---

### Q23: Как настроить hot-reload в Docker?

**A:** Compose Watch (GA с v2.22.0). Три режима: `sync` (копирование файлов), `rebuild` (пересборка), `sync+restart`. Настраивается в секции `develop.watch` compose-файла. Запуск: `docker compose watch`. Также работают bind mounts с инструментами типа uvicorn --reload или Vite.

---

### Q24: containerd image store -- что это?

**A:** Новое хранилище образов на основе containerd (вместо Docker daemon). Дефолт для новых установок Engine 29+. Преимущества: lazy pulling, эффективная дедупликация, поддержка OCI artifacts. Включается через `"containerd-snapshotter": true` в daemon.json.

---

### Q25: Как мониторить контейнеры?

**A:** Базовый: `docker stats` (ресурсы), `docker logs` (логи), HEALTHCHECK. Внешние: healthchecks.io (бесплатно до 20 проверок), UptimeRobot (до 50 мониторов). Полный стек: Prometheus + Grafana (для 10+ сервисов). Docker Debug -- бесплатный shell с инструментами даже в distroless-контейнерах.

---

### Q26: Docker Init -- что это?

**A:** `docker init` -- интерактивный генератор, создающий Dockerfile, compose.yaml и .dockerignore на основе твоего проекта. Появился в Docker Desktop 4.18+. Распознаёт Node.js, Python, Go, Rust, Java. Запусти в корне проекта -- получишь production-ready конфигурацию за 30 секунд. Генерирует multi-stage build, non-root user, healthcheck.

---

### Q27: Docker Bake -- зачем?

**A:** `docker buildx bake` позволяет описать сложные multi-target сборки в HCL-файле (`docker-bake.hcl`). Полезно для: multi-platform, matrix builds, сборка нескольких сервисов одной командой. Замена длинных `docker buildx build` команд с множеством флагов. Поддерживает переменные, группы целей и наследование. Просмотр плана: `docker buildx bake --print`.

---

### Q28: Testcontainers -- как использовать с Docker?

**A:** Testcontainers -- библиотека для интеграционного тестирования, запускающая реальные БД/сервисы в Docker-контейнерах. Доступна для Java, Go, Node.js, Python, .NET. Тесты запускают PostgreSQL/Redis/Kafka в контейнере, выполняют проверки, контейнер удаляется автоматически. Работает с Docker Engine (нет зависимости от Docker Desktop). Идеально для CI/CD pipeline.

---

### Q29: Docker в WSL2 без Docker Desktop?

**A:** Можно. Установи Docker Engine напрямую в WSL2 (Ubuntu): `sudo apt-get install docker-ce docker-ce-cli containerd.io`. Преимущества: бесплатно для коммерческого использования, меньше потребление RAM, нет GUI-оверхеда. Недостатки: нет GUI, нет Docker Scout UI, нет Docker Model Runner, ручная настройка. Для Docker Compose: `sudo apt-get install docker-compose-plugin`. Для VS Code: расширение Remote-WSL работает без Docker Desktop.
