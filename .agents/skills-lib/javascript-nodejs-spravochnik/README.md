# JavaScript & Node.js Production Справочник

Комплексный справочник для разработки современных JavaScript/Node.js приложений с фокусом на production-ready код, serverless функции и full stack приложения.

## Быстрый старт

**5 минут:** Serverless function для бронирования
**10 минут:** Express REST API сервер
**30 минут:** Full stack приложение с PostgreSQL

См. секцию "Quick Start Guide" в SKILL.md

## Структура скилла

```
javascript-nodejs-справочник/
│
├── SKILL.md                    # Главный файл (5144 слова)
├── README.md                   # Этот файл
│
├── references/                 # 8 модульных справочников
│   ├── javascript-fundamentals.md
│   ├── nodejs-basics.md
│   ├── express-api.md
│   ├── serverless-functions.md
│   ├── database-integration.md
│   ├── authentication.md
│   ├── error-handling.md
│   └── testing-deployment.md
│
├── assets/
│   ├── templates/              # 15 production-ready templates
│   │   ├── serverless-function-template.js
│   │   ├── express-server-template.js
│   │   ├── rest-api-route.js
│   │   └── ...
│   │
│   └── examples/               # 15 полных рабочих примеров
│       ├── 01-booking-form-handler/
│       ├── 02-payment-webhook/
│       ├── 03-sheets-api-sync/
│       └── ...
│
├── scripts/                    # 12 production scripts
│   ├── lint.js
│   ├── dev-server.js
│   ├── test.js
│   └── ...
│
└── experience/                 # Система накопления опыта
    ├── _index.md
    ├── fixes/
    ├── improvements/
    ├── patterns/
    └── warnings/
```

## Основные возможности

- **8 References**: Модульные справочники по ключевым темам
- **15 Templates**: Готовые шаблоны для копирования
- **15 Examples**: Полные рабочие примеры с тестами
- **12 Scripts**: Production-ready утилиты
- **Best Practices**: Security, error handling, performance, deployment

## Применение в туристическом бизнесе ОАЭ

Все примеры адаптированы для:
- Формы бронирования туров и экскурсий
- Payment webhooks (Stripe, PayPal)
- Email подтверждения бронирований
- WhatsApp интеграции
- Google Sheets синхронизация
- Multi-currency pricing (AED, USD, RUB, KZT)

## Рекомендуемые пути обучения

**Начинающий (Serverless-first):**
1. javascript-fundamentals.md
2. nodejs-basics.md
3. serverless-functions.md
4. error-handling.md
5. testing-deployment.md

**Опытный (Full Stack):**
1. express-api.md
2. database-integration.md
3. authentication.md
4. error-handling.md
5. testing-deployment.md

**Production (Best Practices):**
1. error-handling.md
2. authentication.md
3. Изучить все templates
4. Применить security-audit.js
5. Настроить monitoring

## Быстрые команды

```bash
# Development
npm run lint          # ESLint проверка
npm run format        # Prettier форматирование
npm run dev           # Dev server с hot reload
npm run type-check    # Type checking

# Testing
npm test              # Jest tests
npm run test:watch    # Watch mode
npm run test:coverage # Coverage report

# Database
npm run migrate       # Run migrations
npm run seed          # Seed data

# Production
npm run build         # Production build
npm run security      # Security audit
npm run deploy        # Deploy
```

## Система накопления опыта

При работе со скиллом:
1. Читайте `experience/_index.md` перед началом
2. Записывайте найденные решения в соответствующие папки
3. Обновляйте топ-5 критических уроков

## Связанные скиллы

- `html-css-справочник` - Frontend формы и UI
- `database-sql-справочник` - PostgreSQL queries
- `netlify-deployment` - Serverless deployment
- `api-туризм-оаэ` - Бизнес логика туризма ОАЭ

## Версия

**Версия:** 1.0
**Дата создания:** 2026-02-04
**Автор:** Сухейль (Dubai Tours)

---

Для детального изучения откройте **SKILL.md**
