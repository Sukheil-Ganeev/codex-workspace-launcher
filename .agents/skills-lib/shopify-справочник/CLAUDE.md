# CLAUDE.md -- shopify-справочник

## Общая информация

- **Название:** shopify-справочник
- **Путь:** `C:/Users/londo/.claude/skills/shopify-справочник/`
- **Версия:** 1.0
- **Дата создания:** 13.02.2026
- **Автор:** Claude Code Agent
- **Для кого:** Сухейль -- туристический бизнес в ОАЭ (Дубай, Tecom)

## Назначение скилла

Production-ready руководство по Shopify e-commerce для туристического бизнеса ОАЭ. Охватывает создание и настройку онлайн-магазина туристических услуг: экскурсии, билеты в парки и на достопримечательности, яхты, трансферы, аренда автомобилей. Включает Shopify API (Admin REST/GraphQL, Storefront), Liquid шаблоны, Apps, мультиязычность (RU/EN/AR), интеграцию платежей (AED/crypto), SEO.

**Когда активировать:** когда нужно создать или настроить онлайн-магазин туристических услуг на Shopify, разобраться с Shopify API, Liquid шаблонами, платежами в ОАЭ, мультиязычностью.

---

## Структура файлов

```
shopify-справочник/
├── CLAUDE.md                       # Этот файл -- мета-описание скилла
├── CHANGELOG.md                    # История изменений
├── SKILL.md                        # Основной справочник (~5000 слов, 14 разделов)
├── README.md                       # Краткое описание + быстрый старт
└── references/
    ├── faq.md                      # 12 часто задаваемых вопросов
    ├── troubleshooting.md          # 12 типичных проблем и решений
    └── cheatsheet.md               # Шпаргалка: CLI, API endpoints, Liquid, Webhooks, тарифы
```

### Описание каждого файла

| Файл | Размер | Описание |
|------|--------|----------|
| `SKILL.md` | ~1188 строк | Основной справочник. 14 разделов от обзора платформы до безопасности. Полный код, примеры, таблицы |
| `README.md` | ~58 строк | Структура проекта, таблица разделов, требования, быстрый старт |
| `references/faq.md` | ~303 строки | 12 вопросов с подробными ответами и примерами кода |
| `references/troubleshooting.md` | ~377 строк | 12 проблем с симптомами, причинами и пошаговыми решениями |
| `references/cheatsheet.md` | ~425 строк | Быстрая справка по CLI, REST API, GraphQL, Liquid, Webhooks, Flow, тарифам |

---

## 14 разделов SKILL.md

### 1. Обзор платформы и бизнес-модель
Shopify для услуг vs товаров (таблица отличий). Тарифные планы 2026 (Starter $5 -- Plus $2300+). Рекомендация: Basic $39 для старта, Grow $105 при обороте >$10K/мес. Почему Shopify для туризма: 4.8 млн магазинов, 130+ валют, 20 языков, PCI DSS Level 1.

### 2. Быстрый старт: Магазин за 1 день
5 шагов: регистрация (3 дня бесплатно, далее $1/мес на 3 мес), создание продуктов-экскурсий (Desert Safari VIP Experience как пример), коллекции (Excursions, Tickets, Yacht Charters, Car Rentals, Transfers, Hot Deals), выбор темы (Dawn бесплатная, Ride $360, Taste $350, Sense $360), домен и запуск.

### 3. Архитектура продуктов для туризма
Структура Product для экскурсии (Burj Khalifa пример). 12 custom metafields для туризма (duration, location, includes, excludes, meeting_point, operating_hours, min/max_participants, cancellation_policy, difficulty_level, languages_available, map_url). Коллекции (ручные и автоматические с условиями). Система тегирования: категория, эмират, время суток, тип группы, особенности, сезон, аудитория.

### 4. Shopify Liquid
Архитектура тем Online Store 2.0 (layout, templates, sections, snippets, assets, config, locales). Основные объекты Liquid (product, variant, collection). Фильтры (money, handleize, strip_html, date, json). Кастомная секция Tour Details с WhatsApp-кнопкой и schema.

### 5. Admin API (REST + GraphQL)
Аутентификация (Custom App vs Public App OAuth 2.0). REST Admin API (legacy): базовый URL, CRUD продуктов, rate limits (40 req/мин Basic, 400 Plus). GraphQL Admin API (рекомендуемый с октября 2024): endpoint, query products, mutation productCreate, rate limits (1000 cost points). Webhooks: подписка через GraphQL, 6 ключевых событий для туризма (ORDERS_CREATE/PAID/CANCELLED/FULFILLED, PRODUCTS_UPDATE, APP_UNINSTALLED), верификация HMAC-SHA256.

### 6. Storefront API -- Headless и виджет бронирования
Storefront API (публичный, токен shp_*). Получение каталога, создание корзины и checkout через GraphQL. Hydrogen (React framework от Shopify для headless). Пример TourCard компонента. Oxygen -- бесплатный хостинг для Hydrogen (глобальный CDN, деплой из GitHub).

### 7. Платёжные системы
Shopify Payments НЕ доступен в ОАЭ. 5 альтернатив: Stripe (2.9%), Telr (2.75%), PayTabs (2.85%), Checkout.com, Amazon Payment Services. Приём RUB/KZT через Manual Payment (Сбер/Kaspi). Криптовалюта (Coinbase Commerce, BitPay, NOWPayments). VAT 5% ОАЭ.

### 8. Мультиязычность (RU/EN/AR)
Shopify Markets (Primary UAE AED EN + международные рынки). Translate & Adapt (бесплатное приложение). Арабский RTL (поддержка в Dawn, CSS для RTL). hreflang для SEO (автоматическая генерация).

### 9. SEO
URL-структура. Schema.org JSON-LD для экскурсий (TouristTrip + Product, AggregateOffer, TravelAgency). Скорость загрузки (WebP, lazy loading, минимизация apps). Блог для SEO.

### 10. Apps для туризма
6 категорий: бронирование/календарь (BookThatApp, Sesami, Tipo, Appointo), отзывы (Judge.me, Loox), upsell/cross-sell (ReConvert, Frequently Bought Together), WhatsApp (Chat + Abandoned Cart, SuperLemon), лояльность (Smile.io, LoyaltyLion), аналитика (Lucky Orange, Lifetimely).

### 11. Аналитика
Shopify Analytics (встроенная: sales, sessions, conversion, AOV). Google Analytics 4 (Measurement ID или Custom Pixels). Facebook/Meta Pixel. Яндекс.Метрика. Воронка для туризма (типичные показатели: View to Cart 8-12%, Cart to Checkout 40-55%, overall 2-5%).

### 12. Автоматизация
Shopify Flow (от плана Grow $105): 4 примера workflow (Telegram уведомление, VIP-тег, автоотмена, запрос отзыва). Zapier/Make для планов без Flow. Shopify CLI (установка, работа с темой dev/push/pull, работа с приложением).

### 13. Практические примеры ОАЭ
4 полных примера: Desert Safari (JSON с variants и metafields), Burj Khalifa (билет с 5 вариантами по времени), яхта с депозитом (30% deposit vs full payment), Webhook -> Telegram (полный Node.js сервер с Express, HMAC-верификацией, отправкой в Telegram Bot API).

### 14. Безопасность и Compliance
PCI DSS Level 1. GDPR/Privacy (cookie banner, Privacy Policy). DTCM -- Department of Tourism Dubai (Trade License, DTCM permit, TRN). Безопасность API (.env, CORS). Защита от мошенничества (Fraud Analysis, Stripe Radar, chargebacks <1%).

---

## 12 вопросов FAQ (references/faq.md)

1. **Можно ли продавать услуги (экскурсии, туры) на Shopify?** -- Да, снять галочку "physical product", использовать variants и booking app
2. **Какой тариф выбрать для туристического бизнеса в Дубае?** -- Basic $39 для старта, Grow $105 при росте, Starter $5 только для ссылок
3. **Работает ли Shopify Payments в ОАЭ?** -- Нет, используйте Stripe/Telr/PayTabs; доп. комиссия 2%/1%/0.6%
4. **Как настроить выбор даты/времени тура?** -- BookThatApp ($15/мес) или Sesami (бесплатный plan)
5. **Как сделать магазин на 3 языках (RU/EN/AR)?** -- Markets + Languages + Translate & Adapt + RTL для арабского
6. **Как настроить депозит (частичную оплату)?** -- Варианты продукта (30% Deposit), Apps, или Draft Orders
7. **Как принимать оплату в RUB/KZT?** -- Manual Payment с инструкциями для Сбер/Kaspi + криптовалюта
8. **Как интегрировать с Telegram/WhatsApp ботом?** -- Webhook ORDERS_CREATE -> Telegram Bot API; SuperLemon для WhatsApp
9. **Какие Apps обязательны для туристического магазина?** -- Must-have: Booking app, Judge.me, Translate & Adapt; рекомендуемые: WhatsApp Chat, ReConvert, Smile.io
10. **Как настроить Schema.org для экскурсий?** -- JSON-LD snippet с типами TouristTrip + Product в теме
11. **REST API vs GraphQL -- что выбрать?** -- GraphQL для новых проектов; REST legacy запрещён для public apps с апреля 2025
12. **Как импортировать каталог из Google Sheets/Notion?** -- CSV (встроенный), Matrixify (Excel), API+скрипт, Zapier/Make

---

## 12 проблем Troubleshooting (references/troubleshooting.md)

1. **Shopify Payments недоступен в ОАЭ** -- Third-party providers (Stripe, Telr, PayTabs); доп. комиссия сверх провайдера
2. **Liquid ошибки: "undefined method" или пустые metafields** -- Создать definition, заполнить данные, правильный путь `.metafields` (не `.metafield`), `.value` для list типов
3. **Валюта отображается неправильно (USD вместо AED)** -- Store currency = AED, Primary market = UAE, правильный Liquid фильтр `| money`
4. **Webhook не приходит или отклоняется** -- HTTPS с валидным SSL, возвращать 200 быстро, raw body для HMAC, 19 ретраев за 48 часов
5. **Rate Limit ошибки (429 Too Many Requests)** -- Throttling, проверка `X-Shopify-Shop-Api-Call-Limit`, Bulk Operations для массовых запросов
6. **Мультиязычность: переводы не отображаются** -- Языки должны быть Published, каждый продукт переводится отдельно, тема с `{{ | t }}` фильтром
7. **Metafields не появляются на странице продукта** -- Dynamic sources в Customize, код в секции, или metafield в section schema
8. **Скорость загрузки низкая (PageSpeed < 50)** -- Удалить неиспользуемые apps, оптимизация изображений (CDN + WebP), Dawn тема, async скрипты
9. **RTL (арабский) отображается некорректно** -- `dir="rtl"` в html, CSS фиксы для flex-direction, margins, breadcrumbs
10. **Корзина: клиент не может завершить checkout** -- Проверить платёжный шлюз, валюту, shipping для digital products, SSL, конфликт apps
11. **Booking app: календарь не появляется на странице продукта** -- Enable booking на продукте, app embed включён, проверить JS-ошибки в консоли
12. **Fulfillment: как отправить email-ваучер вместо посылки** -- Авто-fulfill для digital, custom email notification, Digital Downloads app, API webhook

---

## Структура Cheatsheet (references/cheatsheet.md)

| Секция | Описание |
|--------|----------|
| **Shopify CLI** | Команды для тем (dev, push, pull, list, check, share, package), Hydrogen (create, dev, deploy), приложений (init, dev, deploy, generate extension) |
| **REST Admin API Endpoints** | Products (CRUD, variants, images), Orders (CRUD, cancel, transactions, fulfillments), Customers (CRUD, search, orders), Collections, Other (shop, webhooks, themes, metafields) |
| **GraphQL Admin API** | Products (list, create, update), Orders (list, fulfill), Metafields (set), Webhooks (create, list) |
| **Liquid Quick Reference** | Objects (shop, product, collection, customer, order, request), Tags/Control Flow (if/elsif/else, for, unless, case, assign, capture), Filters (money, handleize, strip_html, date, json, image_url) |
| **Webhook Topics** | Orders (create, updated, paid, cancelled, fulfilled), Products (create, update, delete), Customers (create, update, delete), Other (carts, checkouts, refunds, app/uninstalled, themes, inventory) |
| **Тарифы и лимиты** | Планы (Starter-Plus), API Rate Limits (REST 40 req/мин, GraphQL 1000 points), Store Limits (unlimited products, 2000 variants, 5000 auto collections, 20 languages, 50 markets), Webhooks (5s timeout, 19 retries, HMAC-SHA256) |
| **Shopify Flow** | Common Triggers (8 триггеров), Common Actions (10 действий) |
| **Полезные URL** | Admin, GraphiQL, Docs, Liquid Ref, Theme Check, App Store, Community, Partners, Hydrogen, Status |

---

## Связанная презентация

| Параметр | Значение |
|----------|---------|
| **HTML** | `D:/Downloads/Skill_Presentations/shopify/presentation.html` |
| **PDF** | `D:/Downloads/Skill_Presentations/shopify/output/shopify.pdf` |
| **Тема дизайна** | "Commerce Grid" -- темная с Shopify Green (#95BF47) |
| **Шрифты** | Space Grotesk (заголовки) + Inter (текст) + JetBrains Mono (код) |
| **Размер HTML** | 88 KB |
| **Размер PDF** | 7.7 MB |
| **Количество слайдов** | 18 |

### Список слайдов презентации

| # | Метка | Заголовок |
|---|-------|-----------|
| 1 | E-COMMERCE PLATFORM | Shopify -- E-Commerce Platform 2026 (титульный) |
| 2 | НАВИГАЦИЯ | Содержание -- 18 разделов |
| 3 | АРХИТЕКТУРА | Архитектура Shopify |
| 4 | ТАРИФЫ | Тарифные планы |
| 5 | ШАБЛОНЫ | Liquid -- Шаблонизатор |
| 6 | ТЕМЫ | Структура темы Shopify (Online Store 2.0) |
| 7 | ПРОДУКТ | Продукт-экскурсия |
| 8 | КАТАЛОГ | Коллекции и каталог |
| 9 | CHECKOUT | Checkout Flow |
| 10 | API | Admin API (GraphQL) |
| 11 | STOREFRONT | Storefront API |
| 12 | WEBHOOKS | Webhooks и события |
| 13 | ПЛАТЕЖИ | Платёжные системы ОАЭ |
| 14 | APPS | Apps для туризма |
| 15 | I18N | Мультиязычность RU/EN/AR |
| 16 | SEO | SEO и Schema.org |
| 17 | АВТОМАТИЗАЦИЯ | Аналитика и автоматизация |
| 18 | ЗАПУСК | Чек-лист запуска |

### Дизайн-система презентации

- **Фон:** `#0E1629` (bg-slide), `#0B1222` (bg-dark)
- **Карточки:** `#172038` (bg-card), `#1E2A48` (bg-card-elevated)
- **Акценты:** Shopify Green `#95BF47`, Indigo `#5C6AC4`, Red `#DE3618`, Teal `#00A0AC`
- **Gradient top bar:** `linear-gradient(90deg, #95BF47, #5C6AC4, #00A0AC)`
- **Grid background:** тонкая сетка с шагом 120x160px
- **Ambient glow:** 3 размытых пятна (green, indigo, teal)
- **Glass:** `rgba(255,255,255,0.07)` фон + `rgba(255,255,255,0.12)` бордер
- **Формат:** 1920x1080, padding 70px/100px

---

## Ключевые факты и предупреждения

### Критические для ОАЭ
- **Shopify Payments НЕ доступен в ОАЭ** (на февраль 2026) -- только сторонние шлюзы (Stripe, Telr, PayTabs)
- Без Shopify Payments -- дополнительная комиссия: 2% (Basic), 1% (Grow), 0.6% (Advanced) СВЕРХ комиссии провайдера
- VAT 5% -- Settings -> Taxes, включать в цену рекомендуется
- Нужна Trade License с activity "Tourism" и DTCM permit для онлайн-продажи экскурсий
- Цены в AED -- Store currency и Primary market должны быть настроены на AED

### Технические
- GraphQL API обязателен для новых public apps с апреля 2025. REST = legacy с октября 2024
- Rate Limits: REST 40 req/мин (Basic), GraphQL 1000 cost points (50/сек recovery)
- Webhooks: таймаут 5 секунд, 19 ретраев за 48 часов, HMAC-SHA256 верификация
- Shopify Flow доступен от плана Grow ($105/мес)
- Variants: до 2000 per product (GraphQL), до 100 (REST legacy)
- До 20 языков и 50 рынков (Markets)

### Тарифы (Quick Reference)
- Starter: $5/мес -- только ссылки
- Basic: $39/мес ($29 годовая) -- полный магазин, 2 staff
- Grow: $105/мес ($79 годовая) -- Flow, reports, 5 staff
- Advanced: $399/мес ($299 годовая) -- advanced reports, 15 staff
- Plus: от $2,300/мес -- enterprise
- Retail: $89/мес -- POS-терминал

---

## Связанные скиллы

| Скилл | Связь |
|-------|-------|
| **payment-integration** | Детали по платёжным шлюзам (Stripe, PayTabs), криптовалюта, интеграция |
| **seo** | SEO-стратегии, Schema.org разметка, скорость загрузки |
| **html-css** | Liquid шаблоны используют HTML/CSS; RTL-стилизация |
| **javascript-nodejs** | Webhook-обработчики, Hydrogen (React), Express-серверы |
| **telegram-bot** | Интеграция Shopify -> Telegram (уведомления о заказах через Bot API) |
| **whatsapp-bot** | WhatsApp кнопка на сайте, уведомления через WhatsApp Business API |

---

## Инструкции по использованию

### Активация скилла
1. Прочитать `SKILL.md` -- основной справочник
2. При конкретном вопросе -- проверить `references/faq.md`
3. При проблеме -- проверить `references/troubleshooting.md`
4. Для быстрой справки по командам/API -- `references/cheatsheet.md`

### Типичные сценарии использования
- "Хочу создать магазин на Shopify" -> Раздел 2 (Быстрый старт)
- "Как продавать экскурсии?" -> Раздел 3 (Архитектура продуктов)
- "Как подключить оплату в ОАЭ?" -> Раздел 7 (Платёжные системы)
- "Как сделать сайт на русском и арабском?" -> Раздел 8 (Мультиязычность)
- "Как получать уведомления в Telegram?" -> Раздел 12 (Автоматизация) + Раздел 13 (Примеры)
- "Какие приложения нужны?" -> Раздел 10 (Apps) + FAQ #9

### Обновление скилла
- При изменении тарифов Shopify -- обновить Раздел 1 SKILL.md и cheatsheet.md
- При появлении Shopify Payments в ОАЭ -- обновить Разделы 7, troubleshooting #1, FAQ #3
- При изменении API версии -- обновить Разделы 5, 6, cheatsheet.md
- При появлении новых полезных Apps -- обновить Раздел 10, FAQ #9
- Все изменения фиксировать в CHANGELOG.md

---

## Полезные ссылки

- **Документация Shopify:** https://shopify.dev
- **Liquid Reference:** https://shopify.dev/docs/api/liquid
- **GraphQL Explorer:** https://shopify.dev/docs/api/admin-graphql
- **Theme Store:** https://themes.shopify.com
- **App Store:** https://apps.shopify.com
- **Shopify Community:** https://community.shopify.com
- **Shopify Partners:** https://partners.shopify.com
- **Hydrogen:** https://hydrogen.shopify.dev
- **Status:** https://status.shopify.com
