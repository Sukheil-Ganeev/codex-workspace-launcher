---
name: yandex-cloud-spravochnik
description: "Production-ready руководство по Yandex Cloud для туристического бизнеса ОАЭ. Все сервисы, AI/ML инструменты, IaC. Триггеры - yandex cloud, яндекс облако, yc cli."
version: 1.0.0
author: Сухейль
---
# Yandex Cloud Справочник

## Обзор Yandex Cloud

### Что такое Yandex Cloud

Yandex Cloud — облачная платформа от Яндекса, основной облачный провайдер для российского рынка с полным соответствием законодательству РФ. Запущена в 2018 году, активно развивается и конкурирует с AWS, GCP, Azure.

**Ключевые преимущества:**
- Российская юрисдикция и соответствие 152-ФЗ
- Дата-центры в России (Москва, Владимир, Рязань)
- Поддержка на русском языке 24/7
- Интеграция с экосистемой Яндекса
- Конкурентные цены (часто ниже AWS/GCP)
- Сильные AI/ML сервисы (YandexGPT, SpeechKit, Vision)
- S3-compatible API (легкая миграция с AWS)

**Регионы и зоны доступности:**
- `ru-central1-a` (Москва)
- `ru-central1-b` (Владимир)
- `ru-central1-d` (Рязань)

SLA до 99.95% для критичных сервисов.

### Основные категории сервисов

**Compute (Вычисления):**
- Compute Cloud (виртуальные машины)
- Cloud Functions (serverless)
- Cloud Run (контейнеры)

**Storage (Хранение):**
- Object Storage (S3-compatible)
- Managed Service for PostgreSQL/MySQL/MongoDB/Redis/ClickHouse
- YDB (distributed SQL/NoSQL)

**Networking:**
- Virtual Private Cloud (VPC)
- Load Balancer (L3/L7)
- Cloud DNS
- CDN

**AI/ML:**
- YandexGPT API (генеративные модели)
- SpeechKit (распознавание и синтез речи)
- Vision OCR (распознавание текста)
- Translate (перевод текста)

**Developer Tools:**
- API Gateway (OpenAPI 3.0)
- Message Queue (SQS-compatible)
- Cloud Logging
- Monitoring

**Security & IAM:**
- Identity and Access Management
- Key Management Service (KMS)
- Certificate Manager
- Security Groups

### Compliance и безопасность

- Сертификаты: ISO 27001, PCI DSS Level 1
- Соответствие 152-ФЗ (персональные данные)
- GDPR compliance для международных клиентов
- Шифрование данных at rest и in transit
- DDoS protection включен по умолчанию

### Почему Yandex Cloud для туристического бизнеса в ОАЭ

**Для работы с клиентами из России и СНГ:**
- Оплата в рублях (избегаем валютных рисков)
- Русскоязычная поддержка
- Низкая latency для клиентов из России
- AI инструменты с отличной поддержкой русского языка

**Технические преимущества:**
- Быстрый старт (deploy за минуты)
- Serverless архитектура (pay-as-you-go)
- Managed databases (не нужно администрировать)
- AI/ML сервисы out-of-the-box

**Примеры использования:**
- Booking система с PostgreSQL
- Хранилище фото туров (Object Storage)
- Чат-боты с YandexGPT
- Распознавание голосовых сообщений (SpeechKit)
- OCR для обработки документов

## Quick Start: Deploy за 30 минут

Подробная инструкция в `references/quick-start-30min.md`, но вот краткий путь:

### Шаг 1: Регистрация (5 минут)

```bash
# 1. Перейти на https://cloud.yandex.ru
# 2. Войти через Яндекс ID
# 3. Создать billing account (привязать карту)
# 4. Получить 4000₽ на пробный период (60 дней)
```

### Шаг 2: Установка CLI (5 минут)

```bash
# Linux/macOS
curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash

# Windows (PowerShell)
iex (New-Object System.Net.WebClient).DownloadString('https://storage.yandexcloud.net/yandexcloud-yc/install.ps1')

# Инициализация
yc init
```

### Шаг 3: Первый Cloud Function (10 минут)

```bash
# Создать folder
yc resource-manager folder create --name tourism-dev

# Создать service account
yc iam service-account create --name tourism-sa

# Deploy функции
echo 'module.exports.handler = async (event) => ({ statusCode: 200, body: "Hello from Yandex Cloud!" });' > index.js

yc serverless function create --name hello-tourism
yc serverless function version create \
  --function-name hello-tourism \
  --runtime nodejs18 \
  --entrypoint index.handler \
  --memory 128m \
  --execution-timeout 3s \
  --source-path .
```

### Шаг 4: Public URL (5 минут)

```bash
# Сделать функцию публичной
yc serverless function allow-unauthenticated-invoke hello-tourism

# Получить URL
yc serverless function get hello-tourism --format json | grep http_invoke_url

# Тестировать
curl https://functions.yandexcloud.net/d4e...
```

### Шаг 5: Добавить базу данных (5 минут)

```bash
# Создать PostgreSQL кластер
yc managed-postgresql cluster create \
  --name tourism-db \
  --environment production \
  --network-name default \
  --host zone-id=ru-central1-a,subnet-id=<subnet-id> \
  --postgresql-version 15 \
  --resource-preset s2.micro \
  --disk-type network-ssd \
  --disk-size 10

# Создать базу
yc managed-postgresql database create tourism --cluster-name tourism-db

# Создать пользователя
yc managed-postgresql user create app_user \
  --cluster-name tourism-db \
  --password SecurePass123
```

Полная инструкция: `references/quick-start-30min.md`

## Основные сервисы

### 1. Compute Cloud (Виртуальные машины)

**Когда использовать:**
- Монолитные приложения
- Legacy системы
- Долгоживущие процессы
- Нужен полный контроль над ОС

**Типы инстансов:**
- Standard (balanced CPU/RAM)
- High-Memory (RAM-intensive apps)
- High-Performance (CPU-intensive)
- GPU (ML/AI workloads)

**Preemptible VMs:**
- До 40% дешевле обычных
- Могут быть остановлены через 24 часа
- Идеально для batch-обработки

**Пример use case:** Web-сервер для booking системы

Подробно: `references/compute-cloud-guide.md`

### 2. Object Storage (S3)

**Когда использовать:**
- Статические файлы (фото, видео, документы)
- Backup и архивы
- Data lake
- CDN origin

**Особенности:**
- S3-compatible API (совместимо с AWS SDK)
- Хранение класса Standard, Cold, Ice
- Lifecycle policies (автоматическая миграция)
- Versioning и Object Lock

**Пример use case:** Хранилище фото туров и экскурсий

Подробно: `references/object-storage-s3.md`

### 3. Cloud Functions (Serverless)

**Когда использовать:**
- Event-driven архитектура
- API endpoints
- Scheduled tasks (cron jobs)
- Webhooks

**Поддерживаемые runtime:**
- Node.js 18, 20
- Python 3.11, 3.12
- Go 1.21
- Java 11, 17
- .NET Core 3.1, 6.0
- Bash, PHP 8.2

**Free tier:**
- 1 миллион вызовов/месяц
- 10 ГБ-часов compute time

**Пример use case:** Telegram бот для бронирований

Подробно: `references/serverless-functions.md`

### 4. Managed Databases

**PostgreSQL:**
- Версии 12-16
- Automatic backups
- High Availability (синхронная репликация)
- Connection pooler (Odyssey)

**MySQL:**
- Версии 5.7, 8.0
- Managed replication

**MongoDB:**
- Версии 4.4-7.0
- Sharded clusters

**ClickHouse:**
- OLAP для аналитики
- Петабайтные датасеты

**YDB:**
- Distributed SQL/NoSQL
- Serverless mode

**Пример use case:** PostgreSQL для booking системы

Подробно: `references/databases-guide.md`

### 5. API Gateway

**Когда использовать:**
- Единая точка входа для microservices
- Rate limiting
- Authentication/Authorization
- Request/response трансформация

**Особенности:**
- OpenAPI 3.0 спецификация
- Интеграция с Cloud Functions, Object Storage, YDB
- WebSocket поддержка
- Authorizers (custom auth logic)

**Пример use case:** REST API для мобильного приложения

Подробно: `references/api-gateway-guide.md`

### 6. AI/ML сервисы

**YandexGPT API:**
- YandexGPT 5 Pro (128k context)
- YandexGPT 4 Lite (быстрая версия)
- Streaming responses
- Function calling

**SpeechKit:**
- Распознавание речи (RU, EN, TR и др.)
- Синтез речи (10+ голосов)
- Real-time streaming

**Vision OCR:**
- Распознавание текста на изображениях
- Таблицы, бланки, документы
- 10+ языков

**Translate:**
- 90+ языков
- HTML поддержка

**Пример use case:** Чат-бот с голосовым управлением

Подробно: `references/ai-ml-services.md`

## Структура справочника

### References (подробные руководства)

1. **quick-start-30min.md** - С нуля до первого deploy
2. **compute-cloud-guide.md** - Виртуальные машины
3. **object-storage-s3.md** - S3 хранилище
4. **databases-guide.md** - Все managed БД
5. **serverless-functions.md** - Cloud Functions
6. **api-gateway-guide.md** - API Gateway
7. **networking-security.md** - VPC, Security Groups, Load Balancers
8. **ai-ml-services.md** - YandexGPT, SpeechKit, Vision
9. **iam-authentication.md** - IAM, service accounts, API keys
10. **terraform-iac.md** - Infrastructure as Code
11. **monitoring-backup.md** - Monitoring, alerting, backup
12. **tourism-business-cases.md** - 12 реальных кейсов для туризма

### Assets

**Templates:** Готовые конфигурации для копирования
- PostgreSQL схемы
- Terraform модули
- OpenAPI спецификации
- Monitoring алерты

**Examples:** Полные working примеры
- Booking API (Node.js)
- Photo storage (Python)
- AI chatbot (Telegram)
- Analytics dashboard (ClickHouse)

**Scripts:** Автоматизация рутинных задач
- Установка CLI
- Deploy функций
- Backup БД
- Cost reporting

## Туристические кейсы для ОАЭ

### Кейс 1: Booking API

**Проблема:** Нужна booking система для экскурсий

**Решение:**
- PostgreSQL Managed Service (tours, bookings, payments)
- API Gateway + Cloud Functions (REST API)
- Object Storage (фото туров)
- Yandex Monitoring (alerting)

**Стек:** Node.js + Express + PostgreSQL + S3

**Deployment time:** 2 часа

**Monthly cost:** ~$50-100 (до 10k bookings)

### Кейс 2: AI-powered Telegram бот

**Проблема:** Автоматизировать ответы на вопросы клиентов

**Решение:**
- Cloud Function (Telegram webhook)
- YandexGPT API (генерация ответов)
- PostgreSQL (история чатов)
- SpeechKit (голосовые сообщения)

**Стек:** Node.js + Telegraf + YandexGPT

**Deployment time:** 4 часа

**Monthly cost:** ~$30-60 (1000 диалогов)

### Кейс 3: Photo Storage с CDN

**Проблема:** Хранение и быстрая доставка фото туров клиентам

**Решение:**
- Object Storage (unlimited фото)
- CDN (быстрая доставка globally)
- Vision API (auto-tagging фото)
- Lifecycle policies (архивирование старых фото)

**Стек:** Python + Flask + S3 + CDN

**Deployment time:** 3 часа

**Monthly cost:** ~$20-40 (100GB фото + CDN traffic)

Все 12 кейсов: `references/tourism-business-cases.md`

## Best Practices Чеклист

### Security

- [ ] Используй service accounts вместо OAuth токенов пользователей
- [ ] Применяй least privilege (минимальные permissions)
- [ ] Включи MFA для console доступа
- [ ] Используй Security Groups (firewall rules)
- [ ] Шифруй sensitive данные с помощью KMS
- [ ] Регулярно ротируй API keys
- [ ] Логируй все API calls (Cloud Logging)

### Cost Optimization

- [ ] Используй Preemptible VMs для non-critical workloads
- [ ] Настрой lifecycle policies для Object Storage
- [ ] Мониторь расходы через Billing dashboard
- [ ] Используй serverless где возможно (pay-per-use)
- [ ] Удаляй unused ресурсы (snapshots, disks, IPs)
- [ ] Рассмотри Reserved Instances для production VM

### Performance

- [ ] Используй CDN для статических ресурсов
- [ ] Включи кеширование на уровне API Gateway
- [ ] Настрой connection pooling для БД
- [ ] Используй Load Balancer для распределения нагрузки
- [ ] Мониторь latency через Yandex Monitoring
- [ ] Размещай ресурсы в одной зоне доступности (снижение latency)

### Reliability

- [ ] Включи automatic backups для БД
- [ ] Настрой alerting для критичных метрик
- [ ] Используй High Availability режим для production БД
- [ ] Реализуй retry logic в приложениях
- [ ] Настрой health checks для VM/Load Balancers
- [ ] Тестируй disaster recovery процедуры

### Development

- [ ] Используй Terraform для infrastructure
- [ ] Версионируй infrastructure код в Git
- [ ] Разделяй окружения (dev, staging, production)
- [ ] Используй CI/CD для автоматического deploy
- [ ] Документируй API через OpenAPI specs
- [ ] Логируй структурированные логи (JSON)

### Monitoring

- [ ] Настрой дашборды для ключевых метрик
- [ ] Создай алерты для аномалий
- [ ] Мониторь CPU, RAM, disk, network
- [ ] Отслеживай error rates и latency
- [ ] Логируй все ошибки приложений
- [ ] Регулярно reviewай логи

## Pricing Overview (2026)

### Compute Cloud

**Standard VM (2 vCPU, 4GB RAM):**
- On-demand: ~4,000₽/месяц
- Preemptible: ~2,400₽/месяц (40% discount)

**Storage:**
- SSD: 8₽/GB/месяц
- HDD: 2₽/GB/месяц

### Cloud Functions

**Free tier:**
- 1M invocations/месяц
- 10 GB-часов compute time

**Paid:**
- 1.28₽ за 1M invocations
- 104₽ за 1 GB-час

### Object Storage

**Standard класс:**
- Хранение: 1.93₽/GB/месяц
- GET requests: 0.32₽/10k
- PUT requests: 3.20₽/10k

**Cold класс (архив):**
- 0.64₽/GB/месяц

### Managed PostgreSQL

**s2.micro (2 vCPU, 8GB RAM):**
- ~8,000₽/месяц (production)
- Включает automatic backups

### AI/ML сервисы

**YandexGPT API:**
- Lite: 0.12₽/1k tokens
- Pro: 0.60₽/1k tokens

**SpeechKit:**
- Распознавание: 240₽/час аудио
- Синтез: 960₽/1M символов

**Vision OCR:**
- 120₽/1000 изображений

**Перевод:**
- 480₽/1M символов

Актуальные цены: https://cloud.yandex.ru/prices

## Получение помощи

### Когда читать какой reference

**Только начинаешь:**
1. `quick-start-30min.md` - первый deploy
2. `serverless-functions.md` - простейший сервис
3. `tourism-business-cases.md` - найди похожий кейс

**Создаешь API:**
1. `api-gateway-guide.md` - настройка gateway
2. `serverless-functions.md` - backend функции
3. `databases-guide.md` - выбор БД
4. `iam-authentication.md` - security

**Работаешь с БД:**
1. `databases-guide.md` - выбор и настройка
2. `monitoring-backup.md` - backup стратегия
3. Смотри `assets/templates/booking-system-schema.sql`

**Делаешь AI/ML:**
1. `ai-ml-services.md` - обзор всех сервисов
2. `tourism-business-cases.md` - кейс 2, 4, 9
3. Смотри `assets/examples/ai-chatbot-telegram/`

**Infrastructure as Code:**
1. `terraform-iac.md` - основы Terraform
2. Смотри `assets/templates/terraform-*/`
3. `monitoring-backup.md` - production setup

**Production deploy:**
1. `networking-security.md` - VPC, security groups
2. `monitoring-backup.md` - alerting, backup
3. `terraform-iac.md` - автоматизация
4. Используй `scripts/health-check.sh`

### Официальная документация

- Docs: https://cloud.yandex.ru/docs
- API Reference: https://cloud.yandex.ru/docs/api-design-guide
- Community: https://t.me/yandexcloud
- Support: https://console.cloud.yandex.ru/support

### Полезные ссылки

- Console: https://console.cloud.yandex.ru
- Status: https://status.cloud.yandex.ru
- Blog: https://cloud.yandex.ru/blog
- YouTube: https://www.youtube.com/@YandexCloud

## Яндекс Диск (MCP)

### Обзор

Яндекс Диск -- файловое хранилище Сухейля, доступное через MCP-инструменты. Используется для поиска фото туров, экскурсий, яхт и автомобилей, а также для интеграции с PDF-презентациями.

### Доступные MCP-инструменты (9 штук)

| Инструмент | Назначение |
|-----------|-----------|
| `yandex_disk_info` | Общая информация о диске |
| `yandex_disk_list_files` | Плоский список файлов (limit/offset) |
| `yandex_disk_get_metadata` | Метаданные файла/папки + вложенные items |
| `yandex_disk_get_download_url` | Временная ссылка на скачивание |
| `yandex_disk_get_upload_url` | Ссылка для загрузки |
| `yandex_disk_create_folder` | Создание папки |
| `yandex_disk_copy` | Копирование |
| `yandex_disk_move` | Перемещение |
| `yandex_disk_delete` | Удаление |

### Алгоритм поиска файлов

1. **Начни с `get_metadata("/")`** -- покажет корневые папки
2. **Навигируй вглубь** по названию папок через `get_metadata("/путь")`
3. **Большие папки** (>20 items) -- метаданные сохраняются в файл, парси через Python/jq
4. **Для скачивания** -- `get_download_url` -> `curl -L -o local_path "URL"`
5. **URL временные** -- скачивай сразу, не кэшируй ссылки

### Карта диска Сухейля

```
disk:/
├── CRM системы стран/          # 81 папка по странам
│   └── CRM система (ОАЭ)/     # Главная CRM
│       ├── БИЛЕТЫ/             # 232 аттракциона (каждый = папка с фото)
│       ├── ГРУППОВЫЕ ЭКСКУРСИИ/ # 15 экскурсий
│       │   ├── НА САФАРИ/      # ПУСТАЯ!
│       │   ├── НА ПЛАТИНОВОЕ САФАРИ/ # 6 фото (Platinum Heritage)
│       │   ├── ПО ДУБАЮ/       # Burj Al Arab, Dubai Mall, Madinat Jumeirah
│       │   └── МОРСКОЙ КРУИЗ/  # Фото лодок и круизов
│       ├── ИНДИВИДУАЛЬНЫЕ ЭКСКУРСИИ/ # 35 вариантов
│       │   ├── НА САФАРИ/      # 1 фото: Desert-Safari.jpg
│       │   ├── НА VIP САФАРИ/  # CARAVANSERAI, ROYAL SAHARA, SONARA
│       │   └── МОРСКОЙ КРУИЗ В ДУБАЕ/
│       └── ОТЕЛИ/
├── Яхты для PDF/               # 250 яхт (каждая = папка с фото интерьеров)
├── фирменный стиль Дубаи/     # Брендинг: логотип, визитки, каталог
│   └── Instagram/              # 20 файлов — иконки highlights, НЕ фото!
├── Машины PDF/                 # Авто для PDF каталогов
└── Загрузки/                   # VK обложки
```

### Навигация по структуре папок

**Ключевые точки входа:**
- Фото аттракционов: `disk:/CRM системы стран/CRM система (ОАЭ)/БИЛЕТЫ/`
- Фото групповых туров: `disk:/CRM системы стран/CRM система (ОАЭ)/ГРУППОВЫЕ ЭКСКУРСИИ/`
- Фото индивидуальных туров: `disk:/CRM системы стран/CRM система (ОАЭ)/ИНДИВИДУАЛЬНЫЕ ЭКСКУРСИИ/`
- Яхты: `disk:/Яхты для PDF/`
- Автомобили: `disk:/Машины PDF/`

**Важные нюансы:**
- `Instagram/` в фирменном стиле = иконки highlights, НЕ фотографии
- `НА САФАРИ` (групповые) = ПУСТАЯ папка
- `НА САФАРИ` (индивидуальные) = 1 фото Desert-Safari.jpg

### Интеграция с презентациями

При поиске фото для PDF-презентаций:
1. Фото скачивай в `images/` папку рядом с `presentation.html`
2. В HTML используй `<img src="images/filename.jpg">`
3. CSS: `object-fit: cover` для обрезки по контейнеру
4. Playwright корректно резолвит относительные пути при конвертации

### Критические уроки

Опыт работы с Яндекс Диском (7 уроков): `C:/Users/londo/.claude/skills/yandex-disk-мсп/experience/_index.md`

---

## Roadmap развития справочника

**Версия 1.1 (Q2 2026):**
- Кейсы с Kubernetes (Managed Kubernetes)
- DataSphere (managed Jupyter notebooks)
- Integration с DataLens (BI dashboards)

**Версия 1.2 (Q3 2026):**
- Video Processing API примеры
- IoT Core для tracking туров
- Blockchain integration (если актуально)

**Версия 2.0 (Q4 2026):**
- Multi-cloud strategies (Yandex + AWS/GCP)
- Advanced ML pipelines
- Full microservices architecture

## Feedback и улучшения

Обнаружил ошибку или нашел лучший способ? Используй команду:

```
"запиши в опыт"
```

Формат записи:
```markdown
## [ДАТА] [ТИП: fix/improvement/pattern/warning]

**Проблема:** ...
**Решение:** ...
**Код:** ...
```

Система опыта: `C:/Users/londo/.claude/skills/_experience-system/EXPERIENCE_PROTOCOL.md`

---

**Версия:** 1.0.0
**Автор:** Сухейль
**Дата:** 2026-02-05
**Лицензия:** Proprietary (для внутреннего использования)
