# Yandex Cloud Справочник

Production-ready руководство по Yandex Cloud для туристического бизнеса ОАЭ.

## Структура справочника

```
yandex-cloud-справочник/
├── SKILL.md                          # Главный файл (обзор, quick start, best practices)
├── README.md                         # Этот файл
├── references/                       # Подробные руководства
│   ├── quick-start-30min.md          # С нуля до первого deploy
│   ├── compute-cloud-guide.md        # Виртуальные машины
│   ├── object-storage-s3.md          # S3 хранилище
│   ├── databases-guide.md            # PostgreSQL, MySQL, MongoDB, ClickHouse, YDB
│   ├── serverless-functions.md       # Cloud Functions
│   ├── api-gateway-guide.md          # API Gateway (OpenAPI 3.0)
│   ├── ai-ml-services.md             # YandexGPT, SpeechKit, Vision, Translate
│   ├── iam-authentication.md         # Service accounts, API keys
│   ├── terraform-iac.md              # Infrastructure as Code
│   ├── networking-security.md        # VPC, Security Groups, Load Balancers
│   ├── monitoring-backup.md          # Monitoring, alerting, backup
│   └── tourism-business-cases.md     # 12 реальных кейсов для туризма
│
├── assets/
│   ├── templates/                    # Готовые конфигурации
│   │   ├── booking-system-schema.sql
│   │   ├── terraform-vm-setup/
│   │   ├── terraform-storage-cdn/
│   │   ├── serverless-api-gateway.yaml
│   │   ├── monitoring-alerts.yaml
│   │   └── backup-policy.json
│   │
│   └── examples/                     # Полные working примеры
│       ├── booking-api-nodejs/
│       ├── photo-storage-python/
│       ├── ai-chatbot-telegram/
│       └── analytics-clickhouse/
│
├── scripts/                          # Automation скрипты
│   ├── install-yc-cli.sh
│   ├── setup-service-account.sh
│   ├── deploy-function.sh
│   ├── backup-database.sh
│   └── cost-report.sh
│
└── experience/                       # Накопленный опыт
    └── _index.md                     # Критические уроки
```

## Быстрый старт

### 1. Прочитай SKILL.md

Главный файл содержит:
- Обзор Yandex Cloud
- Quick Start (30 минут)
- Основные сервисы
- Best practices чеклист

### 2. Пройди Quick Start

`references/quick-start-30min.md` - за 30 минут от регистрации до рабочего приложения:
- Создание аккаунта (бонус 4000₽)
- Установка yc CLI
- Первый Cloud Function
- PostgreSQL база данных

### 3. Найди свой кейс

`references/tourism-business-cases.md` - 12 готовых кейсов:
1. Booking API
2. Photo Storage с CDN
3. AI Telegram бот
4. Voice Transcription
5. Multi-currency Payments
6. Analytics Dashboard
7. Disaster Recovery
8. Auto-scaling Web App
9. OCR для документов
10. Real-time Notifications
11. Automated Backups
12. Full-stack IaC (Terraform)

## Навигация по references

### Начинаешь с нуля?

1. `quick-start-30min.md` - первый deploy
2. `serverless-functions.md` - простейший сервис
3. `tourism-business-cases.md` - найди похожий кейс

### Создаешь API?

1. `api-gateway-guide.md` - настройка gateway
2. `serverless-functions.md` - backend функции
3. `databases-guide.md` - выбор БД
4. `iam-authentication.md` - security

### Работаешь с данными?

1. `databases-guide.md` - выбор и настройка БД
2. `object-storage-s3.md` - хранение файлов
3. `monitoring-backup.md` - backup стратегия

### Делаешь AI/ML?

1. `ai-ml-services.md` - YandexGPT, SpeechKit, Vision
2. `tourism-business-cases.md` - кейсы #2, #3, #4, #9
3. `assets/examples/ai-chatbot-telegram/` - полный пример

### Production deploy?

1. `terraform-iac.md` - Infrastructure as Code
2. `networking-security.md` - VPC, security groups
3. `monitoring-backup.md` - alerting, backup

## Assets

### Templates (готовые конфигурации)

Скопируй и адаптируй под свои нужды:
- `booking-system-schema.sql` - PostgreSQL схема для туризма
- `terraform-*/` - Terraform модули
- `serverless-api-gateway.yaml` - OpenAPI spec
- `monitoring-alerts.yaml` - Alerting rules
- `backup-policy.json` - Backup configuration

### Examples (полные примеры)

Working код, готовый к deploy:
- `booking-api-nodejs/` - REST API (Express + PostgreSQL)
- `photo-storage-python/` - S3 upload (Flask)
- `ai-chatbot-telegram/` - Telegram бот (YandexGPT)
- `analytics-clickhouse/` - Analytics dashboard

Каждый example содержит:
- README.md (установка, запуск)
- Исходный код с комментариями
- package.json / requirements.txt
- .env.example
- Инструкция по deploy

## Scripts

Автоматизация рутинных задач:

```bash
# Установка CLI
./scripts/install-yc-cli.sh

# Создание service account + API keys
./scripts/setup-service-account.sh tourism-sa

# Deploy функции
./scripts/deploy-function.sh tourism-api ./src

# Backup БД
./scripts/backup-database.sh tourism-db

# Cost report
./scripts/cost-report.sh
```

Все скрипты имеют:
- Usage help (`-h` flag)
- Error handling
- Примеры использования

## Pricing (примеры для туризма)

### Small setup (стартап)

**Стек:** Cloud Functions + PostgreSQL + S3
- Functions: Free tier (1M calls/month)
- PostgreSQL s2.micro: ~8,000₽/месяц
- S3 (50GB + CDN): ~500₽/месяц

**Итого:** ~8,500₽/месяц (~$90)

### Medium setup (растущий бизнес)

**Стек:** API Gateway + Functions + PostgreSQL + S3 + ClickHouse
- API Gateway: ~500₽/месяц
- Functions: ~1,000₽/месяц
- PostgreSQL s2.small: ~17,000₽/месяц
- S3 (200GB + CDN): ~1,500₽/месяц
- ClickHouse s2.small: ~17,000₽/месяц

**Итого:** ~37,000₽/месяц (~$400)

### Large setup (масштаб)

**Стек:** Instance Group + Load Balancer + PostgreSQL HA + S3 + ClickHouse + YandexGPT
- Instance Group (4 VM): ~16,000₽/месяц
- Load Balancer: ~1,500₽/месяц
- PostgreSQL HA: ~34,000₽/месяц
- S3 (1TB + CDN): ~4,000₽/месяц
- ClickHouse cluster: ~34,000₽/месяц
- YandexGPT: ~2,000₽/месяц

**Итого:** ~91,500₽/месяц (~$1,000)

## Полезные ссылки

**Официальные ресурсы:**
- Console: https://console.cloud.yandex.ru
- Docs: https://cloud.yandex.ru/docs
- API Reference: https://cloud.yandex.ru/docs/api-design-guide
- Pricing: https://cloud.yandex.ru/prices
- Status: https://status.cloud.yandex.ru

**Community:**
- Telegram: https://t.me/yandexcloud
- Blog: https://cloud.yandex.ru/blog
- YouTube: https://www.youtube.com/@YandexCloud

**Support:**
- Console support: https://console.cloud.yandex.ru/support
- Email: cloud@support.yandex.ru

## FAQ

### Как выбрать между VM и Cloud Functions?

**Используй VM если:**
- Монолитное приложение
- Долгоживущие процессы (>10 минут)
- Legacy система
- Нужен полный контроль над ОС

**Используй Cloud Functions если:**
- API endpoints
- Event-driven обработка
- Scheduled tasks
- Stateless приложения

### Какую БД выбрать?

| Задача | Рекомендация |
|--------|-------------|
| Booking система, транзакции | PostgreSQL |
| Аналитика, big data | ClickHouse |
| Session storage, real-time | YDB |
| Flexible schema | MongoDB |
| Кэш | Redis |

### S3 или Compute Storage?

**S3 (Object Storage):**
- Unlimited storage
- S3-compatible API
- CDN integration
- Дешевле (1.93₽/GB vs 8₽/GB)

**Compute Storage (VM диски):**
- Только для VM
- Лучшая производительность для БД
- Snapshots

### Free tier есть?

Да, пробный период:
- 4000₽ на 60 дней (новые аккаунты)
- Cloud Functions: 1M calls/month бесплатно
- Egress traffic: первые 100GB/месяц бесплатно

## Roadmap

**Версия 1.1 (Q2 2026):**
- Kubernetes (Managed Kubernetes)
- DataSphere (managed Jupyter)
- DataLens integration (BI)

**Версия 1.2 (Q3 2026):**
- Video Processing API
- IoT Core
- Advanced ML pipelines

**Версия 2.0 (Q4 2026):**
- Multi-cloud strategies
- Full microservices architecture
- Service mesh (Istio)

## Contribution

Нашел ошибку или хочешь добавить кейс? Используй систему опыта:

```
"запиши в опыт"
```

Протокол: `C:/Users/londo/.claude/skills/_experience-system/EXPERIENCE_PROTOCOL.md`

---

**Версия:** 1.0.0
**Дата:** 2026-02-05
**Автор:** Сухейль
**Лицензия:** Proprietary
