# Registry и CI/CD: полное руководство

> Reference для docker-справочник | Дата: 2026-02-17
> Docker Engine 29.x | Compose v2.40+ (CLI v5.x) | Февраль 2026

---

## 1. Docker Hub

### Тарифные планы (с декабря 2024)

| План | Стоимость | Pull Limit | Приватные репо | Сборки | Scout |
|------|-----------|------------|---------------|--------|-------|
| **Personal** (Free) | $0 | 100/час | 1 | Нет | Ограниченный |
| **Pro** | $9/мес | Безлимитно | Безлимитно | Нет | 3 репо |
| **Team** | $15/юзер/мес | Безлимитно | Безлимитно | Нет | Вся организация |
| **Business** | $24/юзер/мес | Безлимитно | Безлимитно | Нет | + SSO, SCIM, audit logs |

### Rate Limits (с 1 апреля 2025)

| Тип аутентификации | Лимит pulls/час |
|-------------------|-----------------|
| Без аутентификации | **10** (было 100, ужесточено) |
| Personal (бесплатный) | **100** |
| Pro / Team / Business | **Безлимитно** |

**Правило для CI:** всегда авторизуйся. Без `docker login` -- 10 pulls/час, CI упадёт.

```bash
# Авторизация в CI
echo $DOCKER_TOKEN | docker login -u $DOCKER_USER --password-stdin

# Проверка оставшихся pulls
TOKEN=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/nginx:pull" | jq -r .token)
curl -sI -H "Authorization: Bearer $TOKEN" https://registry-1.docker.io/v2/library/nginx/manifests/latest | grep -i ratelimit
```

### Push на Docker Hub

```bash
docker login
docker tag myapp:v1.0 username/myapp:v1.0
docker push username/myapp:v1.0
```

---

## 2. GHCR (GitHub Container Registry)

GHCR (`ghcr.io`) -- реестр от GitHub, интегрирован с GitHub Actions и Packages. `docker.pkg.github.com` **мёртв** с 24 февраля 2025 -- только `ghcr.io`.

### Авторизация

```bash
# Через Personal Access Token (PAT) с правами write:packages
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# В GitHub Actions -- автоматически через secrets.GITHUB_TOKEN
```

### Настройка в workflow

```yaml
permissions:
  contents: read
  packages: write

steps:
  - uses: docker/login-action@v3
    with:
      registry: ghcr.io
      username: ${{ github.actor }}
      password: ${{ secrets.GITHUB_TOKEN }}

  - uses: docker/build-push-action@v6
    with:
      push: true
      tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

### Видимость (Visibility)

| Тип | Pulls | Кто может pull |
|-----|-------|----------------|
| **Public** | Безлимитно, без авторизации | Все |
| **Private** | По авторизации | Только участники org/repo |

**Совет:** для open-source используй public GHCR -- безлимитные pulls без авторизации (в отличие от Docker Hub с лимитом 10/час).

### Очистка старых образов

```bash
# Удалить untagged versions через GitHub CLI
gh api --method DELETE /orgs/{org}/packages/container/{package}/versions/{version_id}
```

Для автоматической очистки: GitHub Action `actions/delete-package-versions`.

---

## 3. Self-hosted Registry

### Registry v3 (GA с июня 2025)

Registry v3 -- полная переработка: OCI-native, garbage collection без простоя, улучшенная производительность. Registry v2 продолжает работать, но v3 рекомендуется для новых установок.

```bash
# Запуск Registry v3
docker run -d -p 5000:5000 --restart=always --name registry \
  -v registry-data:/var/lib/registry \
  registry:3

# Push в локальный registry
docker tag myapp:v1.0 localhost:5000/myapp:v1.0
docker push localhost:5000/myapp:v1.0

# Pull из локального registry
docker pull localhost:5000/myapp:v1.0
```

### Production setup

Для production-ready self-hosted registry:

```yaml
# compose.yaml -- Registry с TLS и аутентификацией
services:
  registry:
    image: registry:3
    ports: ["5000:5000"]
    volumes:
      - registry-data:/var/lib/registry
      - ./certs:/certs:ro
      - ./auth:/auth:ro
    environment:
      REGISTRY_HTTP_TLS_CERTIFICATE: /certs/domain.crt
      REGISTRY_HTTP_TLS_KEY: /certs/domain.key
      REGISTRY_AUTH: htpasswd
      REGISTRY_AUTH_HTPASSWD_REALM: Registry Realm
      REGISTRY_AUTH_HTPASSWD_PATH: /auth/htpasswd
    restart: unless-stopped

volumes:
  registry-data:
```

```bash
# Создание htpasswd файла
docker run --rm --entrypoint htpasswd httpd:2 -Bbn admin secretpass > auth/htpasswd
```

### Enterprise: Harbor (CNCF Graduated)

Для крупных организаций: [Harbor](https://goharbor.io/) -- CNCF Graduated проект. Включает: RBAC, уязвимости (Trivy), репликация, quotas, audit logs, LDAP/OIDC. Установка через Helm Chart.

---

## 4. Docker Scout

Docker Scout анализирует образы на уязвимости, генерирует SBOM и даёт рекомендации по обновлению.

### Команды

```bash
docker scout quickview myapp:latest        # обзор: Critical/High/Medium/Low
docker scout cves myapp:latest             # список CVE
docker scout cves --epss myapp:latest      # CVE с вероятностью эксплуатации (EPSS)
docker scout sbom myapp:latest             # Software Bill of Materials
docker scout recommendations myapp:latest  # рекомендации по base image
```

### EPSS Scoring

**EPSS** (Exploit Prediction Scoring System) показывает вероятность эксплуатации CVE в ближайшие 30 дней. Приоритизируй по EPSS, а не только по CVSS-score:

- EPSS > 0.5 -- немедленно патчи
- EPSS 0.1-0.5 -- в ближайший релиз
- EPSS < 0.1 -- мониторь

### Free Tier

Docker Scout бесплатно: до 3 репозиториев, quickview и cves для любых локальных образов. Pro/Team/Business -- больше репозиториев и CI-интеграция.

### В CI/CD

```yaml
- name: Scout scan
  uses: docker/scout-action@v1
  with:
    command: cves
    image: ghcr.io/${{ github.repository }}:${{ github.sha }}
    exit-code: true    # fail если Critical CVE
    only-severities: critical,high
```

---

## 5. Multi-platform Builds

### Docker Buildx

```bash
# Создай builder с поддержкой multi-platform
docker buildx create --name multibuilder --use --bootstrap

# Собери для двух платформ и push
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/org/app:v1.0 \
  --push .

# Только для одной платформы (локально)
docker buildx build --platform linux/arm64 --load -t myapp:arm64 .
```

### Manifest Lists

Multi-platform образ -- это **manifest list**, указывающий на platform-specific манифесты. Docker клиент автоматически выбирает нужный.

```bash
# Просмотр платформ образа
docker manifest inspect python:3.13-slim-bookworm
# Показывает: linux/amd64, linux/arm64, linux/arm/v7, etc.
```

### QEMU vs Docker Build Cloud

| Метод | Скорость | Стоимость | Когда |
|-------|----------|-----------|-------|
| **QEMU** (эмуляция) | 5-8x медленнее | Бесплатно | CI с простыми образами |
| **Docker Build Cloud** | Нативная | $5/мес (200 мин) | Тяжёлые сборки, prod CI |
| **Self-hosted ARM runner** | Нативная | Стоимость сервера | Oracle Cloud Free Tier ARM |
| **Buildx cross-compile** | Нативная | Бесплатно | Go, Rust (кросс-компиляция без эмуляции) |

**Для туризма ОАЭ:** если деплоишь на Oracle Cloud ARM (Free Tier), собирай `linux/arm64` через QEMU в GitHub Actions. Для тяжёлых билдов (Python с C-extensions) используй Docker Build Cloud или self-hosted ARM runner.

---

## 6. GitHub Actions CI/CD

### Основные Actions

| Action | Версия | Назначение |
|--------|--------|-----------|
| `docker/setup-buildx-action@v3` | v3 | Настройка Buildx builder |
| `docker/login-action@v3` | v3 | Авторизация в registry |
| `docker/build-push-action@v6` | v6 | Сборка и push образа |
| `docker/setup-qemu-action@v3` | v3 | QEMU для multi-platform |
| `docker/metadata-action@v5` | v5 | Генерация тегов и labels |
| `docker/scout-action@v1` | v1 | Сканирование уязвимостей |

### Стратегии кэширования

| Стратегия | Размер кэша | Скорость | Настройка |
|-----------|-------------|----------|-----------|
| **GHA Cache** (`type=gha`) | До 10 GB | Быстрый (GitHub infra) | `cache-from/to: type=gha` |
| **Registry Cache** | Безлимитный | Средний (сеть) | `cache-from/to: type=registry,ref=ghcr.io/org/cache` |
| **Local Cache** | Зависит от runner | Самый быстрый | `cache-from: type=local,src=/tmp/.buildx-cache` |

```yaml
# Рекомендуемый кэш: GHA с mode=max
- uses: docker/build-push-action@v6
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

`mode=max` кэширует **все слои**, включая промежуточные stages -- критически важно для multi-stage builds.

---

## 7. Полный CI/CD Pipeline

Рабочий workflow: build -> test -> scan -> push -> deploy.

```yaml
# .github/workflows/deploy.yml
name: Build, Test & Deploy
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  packages: write

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # === 1. Тесты ===
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          docker compose -f compose.test.yml run --rm app npm test
          docker compose -f compose.test.yml down -v

  # === 2. Сборка + Push ===
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=
            type=raw,value=latest

      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      # === 3. Сканирование ===
      - uses: docker/scout-action@v1
        with:
          command: cves
          image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          only-severities: critical,high

  # === 4. Деплой ===
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/myapp
            echo ${{ secrets.GHCR_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f
            # Healthcheck
            sleep 10
            curl -sf http://localhost:8000/health || (docker compose logs --tail=50 && exit 1)
```

---

## 8. Деплой на сервер

### SSH Deploy

Самый простой способ -- SSH action в GitHub Actions (см. pipeline выше). Подходит для 1-3 VPS.

### Docker Context (remote daemon)

```bash
# Создай контекст для удалённого сервера
docker context create oracle --docker "host=ssh://ubuntu@oracle.example.com"
docker context use oracle

# Теперь все docker-команды выполняются на удалённом сервере
docker compose up -d
docker ps
```

### Автоматическое обновление образов

**Watchtower ARCHIVED** (декабрь 2025). Несовместим с Docker 28+/29+. Альтернативы:

| Инструмент | Что делает | Когда |
|------------|-----------|-------|
| **What's Up Docker (WUD)** | Мониторинг + обновление + dashboard | Нужно авто-обновление |
| **DIUN** | Только нотификации (Slack, Telegram, email) | Нужен контроль перед обновлением |
| **CI/CD pipeline** | Push -> auto-deploy | **Рекомендуется для production** |

```yaml
# WUD в Docker Compose
services:
  wud:
    image: fmartinou/whats-up-docker
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      WUD_TRIGGER_DOCKER_COMPOSE_ENABLE: "true"
    restart: unless-stopped
```

### Деплой на Oracle Cloud Free Tier (ARM)

Идеально для туристического бизнеса ОАЭ -- бесплатный ARM-сервер (до 4 OCPU + 24 GB RAM):

1. Собери `linux/arm64` образ в GitHub Actions (QEMU или Build Cloud)
2. Push в GHCR (public = безлимитные pulls)
3. SSH deploy: `docker compose pull && docker compose up -d`
4. Nginx reverse proxy для webhook (WhatsApp, Telegram)

```bash
# На Oracle Cloud сервере
cd /opt/booking-bot
docker compose pull
docker compose up -d --remove-orphans
docker image prune -f

# Проверка
docker compose ps
curl -sf http://localhost:8000/health
```

Скрипт автоматического деплоя с healthcheck и rollback: `scripts/deploy-compose.sh`.

---

> **Связанные файлы:**
> - `cheatsheet.md` -- команды Docker Hub, GHCR, Buildx, Scout
> - `security-production.md` -- Docker Scout, подпись образов, production checklist
> - `networking-volumes.md` -- сети для CI/CD, volume backup
> - SKILL.md -- модули 7 (Registry), 9 (CI/CD)
> - `assets/templates/.github/workflows/docker-ci.yml` -- готовый workflow
> - `assets/examples/05-ci-cd-pipeline/` -- полный пример CI/CD
