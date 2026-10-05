---
name: shopify-spravochnik
description: "Production-ready руководство по Shopify e-commerce для туристического бизнеса ОАЭ. Магазин туров, билетов, яхт, трансферов. Shopify API (Admin REST/GraphQL, Storefront), Liquid шаблоны, Apps, мультиязычность (RU/EN/AR), интеграция платежей (AED/crypto), SEO. Используй когда нужно создать или настроить онлайн-магазин туристических услуг на Shopify."
---
# Shopify E-Commerce -- Магазин туристических услуг ОАЭ

## 1. Обзор платформы и бизнес-модель

### Shopify для услуг vs товаров

Shopify изначально создан для физических товаров, но отлично подходит для продажи **услуг** (экскурсий, билетов, яхт, трансферов). Ключевые адаптации:

| Аспект | Товары | Услуги (туризм) |
|--------|--------|-----------------|
| **Доставка** | Физическая | Отключена (digital/service) |
| **Инвентарь** | Штуки на складе | Слоты дат/времени |
| **Варианты** | Размер/цвет | Дата/группа/VIP-уровень |
| **Fulfillment** | Курьер/почта | Email-ваучер/QR-код |
| **Metafields** | Вес/материал | Длительность/маршрут/включено |

### Тарифные планы (2026)

| План | Месяц | Год (скидка 25%) | Комиссия карт | Особенности |
|------|-------|------------------|---------------|-------------|
| **Starter** | $5 | -- | 5% | Ссылки, соцсети, без магазина |
| **Basic** | $39 | $29/мес | 2.9% + $0.30 | Полный магазин, 2 сотрудника |
| **Grow** | $105 | $79/мес | 2.7% + $0.30 | 5 сотрудников, отчёты |
| **Advanced** | $399 | $299/мес | 2.5% + $0.30 | 15 сотрудников, advanced reports |
| **Plus** | от $2,300 | по договору | 2.15% + $0.30 | Enterprise, 200+ локаций |
| **Retail** | $89 | -- | -- | POS-терминал (офис в Tecom) |

**Рекомендация для туризма ОАЭ:** Basic ($39/мес) для старта, Grow ($105/мес) при обороте >$10K/мес.

### Почему Shopify для туризма

- Более 4.8 млн магазинов, доверие клиентов к checkout
- 130+ валют, включая AED
- 20 языков на одном магазине (RU/EN/AR)
- Apps для бронирования с календарём
- Встроенная аналитика и SEO
- PCI DSS Level 1 (безопасность платежей)

---

## 2. Быстрый старт: Магазин за 1 день

### Шаг 1: Регистрация и настройка

1. shopify.com -> Start free trial (3 дня бесплатно, далее $1/мес на 3 месяца)
2. Settings -> Store details: название, адрес (Дубай, Tecom), валюта AED
3. Settings -> Markets -> Primary market: UAE
4. Settings -> Languages -> Add language: Russian, Arabic

### Шаг 2: Создание продуктов-экскурсий

```
Products -> Add product:
  Title: "Desert Safari VIP Experience"
  Description: (HTML-описание с фото, маршрутом, included)
  Product type: "Tour"
  Vendor: "Dubai Tours by Suheil"
  Tags: desert-safari, adventure, evening, pickup-included

  Pricing:
    Price: 350 AED
    Compare at price: 450 AED (зачёркнутая "старая" цена)

  Variants:
    Option 1: "Group" -> Shared (180 AED) / Private (350 AED) / VIP (550 AED)
    Option 2: "Date" -> (через booking app)

  Shipping: UNCHECK "This is a physical product"

  SEO:
    Page title: "Desert Safari Dubai - VIP Private Tour from 350 AED"
    URL handle: desert-safari-dubai-vip
    Meta description: "Book private desert safari in Dubai..."
```

### Шаг 3: Коллекции

```
Products -> Collections:
  - "Excursions" (tag: excursion)
  - "Tickets & Attractions" (tag: ticket)
  - "Yacht Charters" (tag: yacht)
  - "Car Rentals" (tag: car-rental)
  - "Transfers" (tag: transfer)
  - "Hot Deals" (tag: hot-deal, автоматическая по Compare at price)
```

### Шаг 4: Тема и дизайн

Рекомендуемые темы для туризма:
- **Dawn** (бесплатная) -- минимализм, быстрая, Online Store 2.0
- **Ride** ($360) -- для услуг, бронирование
- **Taste** ($350) -- визуальная, для впечатлений
- **Sense** ($360) -- premium feel

### Шаг 5: Домен и запуск

```
Settings -> Domains:
  - Купить через Shopify: dubaitours.shop ($14/год)
  - Или подключить свой: tours.yourdomain.com (CNAME -> shops.myshopify.com)
```

---

## 3. Архитектура продуктов для туризма

### Структура Product для экскурсии

```
Product
├── Title: "Burj Khalifa At The Top (124 + 125 Floor)"
├── Body HTML: описание + что включено + расписание
├── Product Type: "Ticket"
├── Vendor: "Dubai Attractions"
├── Tags: ["burj-khalifa", "ticket", "downtown", "observation"]
├── Variants:
│   ├── Adult (260 AED)
│   ├── Child 4-12 (210 AED)
│   └── Child 0-3 (Free)
├── Metafields:
│   ├── custom.duration: "1.5 hours"
│   ├── custom.location: "Downtown Dubai"
│   ├── custom.includes: ["Ticket", "Audio Guide"]
│   ├── custom.meeting_point: "Burj Khalifa, Lower Ground Floor"
│   ├── custom.operating_hours: "08:00 - 00:00"
│   └── custom.cancellation_policy: "Free cancellation 24h before"
└── Images: 5-8 фото, alt-теги с ключевыми словами
```

### Metafields для туризма

Settings -> Custom data -> Products -> Add definition:

| Namespace.Key | Тип | Описание |
|---------------|-----|----------|
| `custom.duration` | Single line text | "2 hours", "Full day" |
| `custom.location` | Single line text | Место проведения |
| `custom.includes` | List of single line text | Что входит |
| `custom.excludes` | List of single line text | Что не входит |
| `custom.meeting_point` | Single line text | Точка встречи |
| `custom.operating_hours` | Single line text | Часы работы |
| `custom.min_participants` | Integer | Мин. участников |
| `custom.max_participants` | Integer | Макс. участников |
| `custom.cancellation_policy` | Multi-line text | Политика отмены |
| `custom.difficulty_level` | Single line text | easy/medium/hard |
| `custom.languages_available` | List of single line text | RU, EN, AR |
| `custom.map_url` | URL | Ссылка на Google Maps |

### Collections (Коллекции)

**Ручные коллекции:**
- "Staff Picks" -- рекомендации команды
- "Best Sellers" -- топ продаж

**Автоматические коллекции (по условиям):**
```
"Экскурсии до 200 AED":
  Product type IS "Tour" AND Price IS LESS THAN 200

"Weekend Specials":
  Tag IS "weekend" AND Inventory IS GREATER THAN 0

"VIP Experiences":
  Tag IS "vip" AND Price IS GREATER THAN 500
```

### Tags -- система тегирования

```
Категория:   excursion, ticket, yacht, transfer, car-rental
Эмират:      dubai, abu-dhabi, sharjah, ras-al-khaimah, fujairah
Время суток: morning, afternoon, evening, full-day
Тип группы:  shared, private, vip
Особенности: pickup-included, lunch-included, photo-included
Сезон:       winter-special, summer-deal, ramadan
Аудитория:   family, couples, adventure, luxury
```

---

## 4. Shopify Liquid

### Архитектура тем (Online Store 2.0)

```
theme/
├── layout/
│   └── theme.liquid          # Главный layout (<html>, <head>, <body>)
├── templates/
│   ├── index.json            # Главная страница
│   ├── product.json          # Страница продукта
│   ├── collection.json       # Страница коллекции
│   └── page.json             # Статические страницы
├── sections/
│   ├── header.liquid         # Шапка
│   ├── footer.liquid         # Подвал
│   ├── product-info.liquid   # Информация о продукте
│   ├── tour-details.liquid   # Кастомная секция для туров
│   └── featured-tours.liquid # Подборка туров
├── snippets/
│   ├── tour-card.liquid      # Карточка тура
│   ├── price-badge.liquid    # Бейдж цены
│   └── whatsapp-button.liquid # Кнопка WhatsApp
├── assets/
│   ├── theme.css
│   └── theme.js
├── config/
│   └── settings_schema.json  # Настройки темы
└── locales/
    ├── en.default.json       # Английские переводы
    ├── ru.json               # Русские переводы
    └── ar.json               # Арабские переводы
```

### Основные объекты Liquid

```liquid
{{ product.title }}              <!-- Название продукта -->
{{ product.price | money }}      <!-- Цена в валюте магазина -->
{{ product.description }}        <!-- Описание (HTML) -->
{{ product.featured_image | image_url: width: 800 }}  <!-- Картинка -->
{{ product.metafields.custom.duration }}  <!-- Metafield -->
{{ product.variants.first.price | money }}  <!-- Цена первого варианта -->

{% for variant in product.variants %}
  {{ variant.title }} - {{ variant.price | money }}
{% endfor %}

{% if product.compare_at_price > product.price %}
  <span class="sale-badge">-{{ product.compare_at_price | minus: product.price | money }} OFF</span>
{% endif %}
```

### Фильтры Liquid

```liquid
{{ product.price | money }}                    <!-- 350.00 AED -->
{{ product.price | money_with_currency }}       <!-- 350.00 AED -->
{{ product.title | downcase | handleize }}       <!-- desert-safari-vip -->
{{ product.description | strip_html | truncate: 160 }}  <!-- SEO description -->
{{ "now" | date: "%Y-%m-%d" }}                  <!-- 2026-02-13 -->
{{ product.images | size }}                     <!-- Количество фото -->
{{ product.tags | join: ", " }}                 <!-- tag1, tag2, tag3 -->
```

### Кастомная секция: Tour Details

```liquid
{% comment %} sections/tour-details.liquid {% endcomment %}
{% schema %}
{
  "name": "Tour Details",
  "tag": "section",
  "class": "tour-details",
  "settings": [
    {
      "type": "checkbox",
      "id": "show_whatsapp",
      "label": "Show WhatsApp button",
      "default": true
    },
    {
      "type": "text",
      "id": "whatsapp_number",
      "label": "WhatsApp Number",
      "default": "+971501234567"
    }
  ],
  "blocks": [
    {
      "type": "detail_item",
      "name": "Detail",
      "settings": [
        {
          "type": "text",
          "id": "icon",
          "label": "Icon emoji"
        },
        {
          "type": "text",
          "id": "label",
          "label": "Label"
        },
        {
          "type": "text",
          "id": "value",
          "label": "Value"
        }
      ]
    }
  ]
}
{% endschema %}

<div class="tour-details-grid">
  {% if product.metafields.custom.duration %}
    <div class="detail-item">
      <span class="detail-icon">&#9200;</span>
      <span class="detail-label">{{ 'tour.duration' | t }}</span>
      <span class="detail-value">{{ product.metafields.custom.duration }}</span>
    </div>
  {% endif %}

  {% if product.metafields.custom.location %}
    <div class="detail-item">
      <span class="detail-icon">&#128205;</span>
      <span class="detail-label">{{ 'tour.location' | t }}</span>
      <span class="detail-value">{{ product.metafields.custom.location }}</span>
    </div>
  {% endif %}

  {% if product.metafields.custom.includes %}
    <div class="detail-includes">
      <h3>{{ 'tour.whats_included' | t }}</h3>
      <ul>
        {% for item in product.metafields.custom.includes.value %}
          <li>{{ item }}</li>
        {% endfor %}
      </ul>
    </div>
  {% endif %}

  {% if section.settings.show_whatsapp %}
    <a href="https://wa.me/{{ section.settings.whatsapp_number | remove: '+' }}?text={{ 'tour.whatsapp_message' | t | url_encode }}%20{{ product.title | url_encode }}"
       class="whatsapp-book-btn" target="_blank">
      {{ 'tour.book_whatsapp' | t }}
    </a>
  {% endif %}
</div>
```

---

## 5. Admin API (REST + GraphQL)

### Аутентификация

**Custom App (для своего магазина):**
1. Settings -> Apps and sales channels -> Develop apps -> Create an app
2. Configure Admin API scopes: `read_products`, `write_products`, `read_orders`, `write_orders`
3. Install app -> Get Admin API access token

**Public App (для Shopify App Store):**
OAuth 2.0 flow -> перенаправление на `https://{shop}.myshopify.com/admin/oauth/authorize`

### REST Admin API (legacy, поддерживается)

**Базовый URL:**
```
https://{shop}.myshopify.com/admin/api/2025-01/{resource}.json
```

**Получить продукты:**
```bash
curl -X GET "https://myshop.myshopify.com/admin/api/2025-01/products.json" \
  -H "X-Shopify-Access-Token: {ACCESS_TOKEN}"
```

**Создать продукт-экскурсию:**
```bash
curl -X POST "https://myshop.myshopify.com/admin/api/2025-01/products.json" \
  -H "X-Shopify-Access-Token: {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "product": {
      "title": "Desert Safari Premium",
      "body_html": "<h2>VIP Desert Safari Experience</h2><p>Private 4x4 dune bashing...</p>",
      "vendor": "Dubai Tours",
      "product_type": "Tour",
      "tags": "desert-safari, adventure, evening, pickup-included",
      "variants": [
        {"title": "Shared Group", "price": "180.00", "sku": "DS-SHARED"},
        {"title": "Private (1-6 pax)", "price": "350.00", "sku": "DS-PRIVATE"},
        {"title": "VIP (1-4 pax)", "price": "550.00", "sku": "DS-VIP"}
      ],
      "images": [
        {"src": "https://cdn.example.com/desert-safari-hero.jpg"}
      ]
    }
  }'
```

**Rate Limits (REST):**

| План | Запросов/мин | Восстановление |
|------|-------------|----------------|
| Basic/Grow | 40 | 2 req/сек |
| Advanced | 40 | 4 req/сек |
| Plus | 400 | 20 req/сек |

Заголовок ответа: `X-Shopify-Shop-Api-Call-Limit: 32/40`

### GraphQL Admin API (рекомендуемый)

**С октября 2024** REST считается legacy. Новые public apps обязаны использовать GraphQL.

**Endpoint:**
```
POST https://{shop}.myshopify.com/admin/api/2025-01/graphql.json
```

**Запрос продуктов:**
```graphql
query {
  products(first: 10, query: "product_type:Tour") {
    edges {
      node {
        id
        title
        handle
        priceRangeV2 {
          minVariantPrice { amount currencyCode }
          maxVariantPrice { amount currencyCode }
        }
        metafields(first: 5) {
          edges {
            node {
              namespace
              key
              value
            }
          }
        }
        variants(first: 10) {
          edges {
            node {
              title
              price
              sku
            }
          }
        }
      }
    }
  }
}
```

**Создание продукта (mutation):**
```graphql
mutation {
  productCreate(input: {
    title: "Burj Khalifa Ticket - At The Top"
    descriptionHtml: "<p>Skip-the-line ticket to observation deck...</p>"
    productType: "Ticket"
    vendor: "Dubai Attractions"
    tags: ["burj-khalifa", "ticket", "downtown"]
    variants: [
      { title: "Adult", price: "260.00", sku: "BK-ADULT" }
      { title: "Child 4-12", price: "210.00", sku: "BK-CHILD" }
    ]
  }) {
    product { id title handle }
    userErrors { field message }
  }
}
```

**Rate Limits (GraphQL):**
- Leaky bucket: 1,000 cost points
- Восстановление: 50 points/сек
- Простой запрос: ~10 points, сложный: до 1,000
- Заголовок: `X-GraphQL-Cost-Include-Fields` для отладки

### Webhooks

**Подписка через API:**
```graphql
mutation {
  webhookSubscriptionCreate(
    topic: ORDERS_CREATE
    webhookSubscription: {
      callbackUrl: "https://yourdomain.com/webhooks/orders"
      format: JSON
    }
  ) {
    webhookSubscription { id }
    userErrors { field message }
  }
}
```

**Ключевые события для туризма:**

| Topic | Когда | Действие |
|-------|-------|----------|
| `ORDERS_CREATE` | Новый заказ | Отправить ваучер, уведомить в Telegram |
| `ORDERS_PAID` | Оплата прошла | Подтвердить бронирование |
| `ORDERS_CANCELLED` | Отмена заказа | Освободить слот, вернуть деньги |
| `ORDERS_FULFILLED` | Выполнен | Запросить отзыв через 24ч |
| `PRODUCTS_UPDATE` | Продукт изменён | Синхронизировать с CRM |
| `APP_UNINSTALLED` | App удалён | Cleanup |

**Верификация webhook:**
```javascript
const crypto = require('crypto');

function verifyShopifyWebhook(req) {
  const hmac = req.headers['x-shopify-hmac-sha256'];
  const hash = crypto
    .createHmac('sha256', process.env.SHOPIFY_WEBHOOK_SECRET)
    .update(req.rawBody)
    .digest('base64');
  return crypto.timingSafeEqual(Buffer.from(hmac), Buffer.from(hash));
}
```

---

## 6. Storefront API -- Headless и виджет бронирования

### Storefront API

Storefront API -- публичный API для кастомных витрин (headless), мобильных приложений, виджетов бронирования.

**Токен:** Settings -> Apps -> Develop apps -> Storefront API access token (начинается с `shp_`)

**Получение каталога:**
```graphql
query {
  products(first: 20, query: "product_type:Tour") {
    edges {
      node {
        id
        title
        handle
        description
        priceRange {
          minVariantPrice { amount currencyCode }
        }
        images(first: 1) {
          edges {
            node { url altText }
          }
        }
        metafield(namespace: "custom", key: "duration") {
          value
        }
      }
    }
  }
}
```

**Создание корзины и checkout:**
```graphql
mutation {
  cartCreate(input: {
    lines: [
      { merchandiseId: "gid://shopify/ProductVariant/12345", quantity: 2 }
    ]
    buyerIdentity: {
      email: "tourist@example.com"
      countryCode: AE
    }
  }) {
    cart {
      id
      checkoutUrl
      estimatedCost {
        totalAmount { amount currencyCode }
      }
    }
    userErrors { field message }
  }
}
```

### Hydrogen (Headless React Framework)

Hydrogen -- React-framework от Shopify для headless storefronts. Построен на React Router (бывший Remix).

**Когда использовать:**
- Кастомный UI бронирования с календарём
- Мультибрендовый портал (экскурсии + яхты + авто)
- Интеграция с внешними системами (CRM, PuzzleBot)
- Максимальная производительность (SSR + streaming)

**Быстрый старт:**
```bash
npm create @shopify/hydrogen@latest -- --template demo-store
cd my-tour-store
npm run dev
```

**Пример компонента TourCard:**
```jsx
import {Image, Money} from '@shopify/hydrogen';

export function TourCard({product}) {
  return (
    <div className="tour-card">
      <Image data={product.images.edges[0].node} sizes="(min-width: 768px) 33vw, 100vw" />
      <h3>{product.title}</h3>
      <Money data={product.priceRange.minVariantPrice} />
      <p>{product.metafield?.value}</p>
      <a href={`/tours/${product.handle}`}>Book Now</a>
    </div>
  );
}
```

**Oxygen** -- бесплатный хостинг от Shopify для Hydrogen. Глобальный CDN, автоматический деплой из GitHub.

---

## 7. Платёжные системы

### Shopify Payments в ОАЭ

**Shopify Payments НЕ доступен в ОАЭ** (на февраль 2026). Используйте сторонние шлюзы.

### Альтернативы для ОАЭ

| Gateway | Комиссия | Особенности | Лучше для |
|---------|----------|-------------|-----------|
| **Stripe** | 2.9% + $0.30 | Мгновенная интеграция, 135+ валют, Radar | Международные карты |
| **Telr** | 2.75% + flat | Локальный, AED-first, местные банки | Карты ОАЭ |
| **PayTabs** | 2.85% + $0.30 | Fraud prevention, арабский UI | GCC-регион |
| **Checkout.com** | по договору | Enterprise, низкие ставки при объёме | Высокий оборот |
| **Amazon Payment Services** | 2.75% | Бывший PayFort, доверие | Местный рынок |

**Подключение (Settings -> Payments -> Add payment methods):**

1. Выберите провайдера (Stripe, Telr, PayTabs)
2. Введите API keys
3. Настройте Test mode для проверки
4. Переключите в Live mode

### Приём RUB/KZT (Manual Payment)

```
Settings -> Payments -> Manual payment methods -> Create custom payment method:
  Name: "Bank Transfer (RUB/KZT)"
  Additional details: "Transfer to Sberbank / Kaspi. Send receipt via WhatsApp."
  Payment instructions:
    "Sberbank: 1234 5678 9012 3456 (Имя Получателя)
     Kaspi: +7 777 123 4567
     Reference: Order #{order_number}
     Send screenshot to WhatsApp: +971501234567"
```

### Криптовалюта

Через Shopify Apps: **Coinbase Commerce**, **BitPay**, **NOWPayments**.

```
Apps -> Search "crypto payments" -> Install NOWPayments:
  - Принимает USDT, BTC, ETH, 300+ crypto
  - Автоконвертация в AED/USD
  - Комиссия: 0.5-1%
```

### VAT 5% (ОАЭ)

```
Settings -> Taxes and duties:
  - Country: United Arab Emirates
  - Tax rate: 5%
  - Include tax in prices: YES (рекомендуется)
  - Tax Registration Number (TRN): вводите свой
```

---

## 8. Мультиязычность (RU/EN/AR)

### Shopify Markets

```
Settings -> Markets:
  Primary: United Arab Emirates (AED, EN)

  International markets:
    - Russia & CIS: RU язык, USD валюта
    - Kazakhstan: RU язык, KZT валюта
    - Europe: EN язык, EUR валюта
    - Arab countries: AR язык, AED валюта
```

### Translate & Adapt (бесплатное приложение Shopify)

1. Apps -> Shopify Translate & Adapt -> Install
2. Добавьте языки: Russian (ru), Arabic (ar)
3. Переведите: Products, Collections, Pages, Navigation, Theme
4. URL: `/ru/products/desert-safari`, `/ar/products/desert-safari`

### Арабский язык и RTL

**Тема должна поддерживать RTL.** Dawn поддерживает из коробки.

```liquid
{% comment %} layout/theme.liquid {% endcomment %}
<html lang="{{ request.locale.iso_code }}"
      dir="{{ request.locale.iso_code | slice: 0, 2 | replace: 'ar', 'rtl' | replace: 'he', 'rtl' | default: 'ltr' }}">
```

**CSS для RTL:**
```css
[dir="rtl"] .tour-card { text-align: right; }
[dir="rtl"] .price-badge { left: auto; right: 12px; }
[dir="rtl"] .breadcrumb li + li::before { content: "\\"; }
```

### hreflang для SEO

Shopify автоматически генерирует hreflang при включённых Markets:
```html
<link rel="alternate" hreflang="en" href="https://shop.com/products/desert-safari" />
<link rel="alternate" hreflang="ru" href="https://shop.com/ru/products/desert-safari" />
<link rel="alternate" hreflang="ar" href="https://shop.com/ar/products/desert-safari" />
<link rel="alternate" hreflang="x-default" href="https://shop.com/products/desert-safari" />
```

---

## 9. SEO

### URL-структура

Shopify автоматически генерирует SEO-friendly URL:
```
/collections/excursions
/products/desert-safari-dubai-vip
/pages/about-us
/blogs/dubai-guide/top-10-attractions
```

### Schema.org для экскурсий (JSON-LD)

```liquid
{% comment %} snippets/schema-tourist-trip.liquid {% endcomment %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": ["TouristTrip", "Product"],
  "name": {{ product.title | json }},
  "description": {{ product.description | strip_html | truncate: 500 | json }},
  "url": {{ canonical_url | json }},
  "image": {{ product.featured_image | image_url: width: 1200 | json }},
  "touristType": ["Adventure", "Cultural"],
  "itinerary": {
    "@type": "ItemList",
    "itemListElement": [
      {
        "@type": "TouristAttraction",
        "name": "Dubai Desert",
        "address": {
          "@type": "PostalAddress",
          "addressLocality": "Dubai",
          "addressCountry": "AE"
        }
      }
    ]
  },
  "offers": {
    "@type": "AggregateOffer",
    "priceCurrency": "AED",
    "lowPrice": {{ product.price_min | money_without_currency | json }},
    "highPrice": {{ product.price_max | money_without_currency | json }},
    "offerCount": {{ product.variants.size }},
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "TravelAgency",
      "name": "Dubai Tours by Suheil",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "Tecom, Barsha Heights",
        "addressLocality": "Dubai",
        "addressCountry": "AE"
      },
      "telephone": "+971501234567"
    }
  },
  "provider": {
    "@type": "TravelAgency",
    "name": "Dubai Tours by Suheil"
  }
}
</script>
```

### Скорость загрузки

- Оптимизируйте изображения: Shopify CDN автоматически конвертирует в WebP
- Lazy loading: `loading="lazy"` на изображениях ниже fold
- Минимизируйте apps (каждое добавляет JS)
- Используйте `{{ 'theme.css' | asset_url | stylesheet_tag }}` -- CDN

### Блог для SEO

```
Online Store -> Blog posts -> Create blog post:
  Title: "10 Best Desert Safari Tours in Dubai 2026"
  Tags: dubai, desert-safari, guide
  SEO Title: "Best Desert Safari Dubai 2026 - Prices from 180 AED"
  Meta description: "Complete guide to desert safari..."
```

---

## 10. Apps для туризма

### Бронирование и календарь

| App | Цена | Особенности |
|-----|------|-------------|
| **BookThatApp** | от $15/мес | Календарь, ремайндеры, SMS, групповые |
| **Sesami** | от $0 (free plan) | Omnichannel, Google Calendar, красивый UI |
| **Tipo** | от $0 (free plan) | Простой, кастомные формы |
| **Appointo** | от $10/мес | Zoom-интеграция, Google Calendar |

### Отзывы

| App | Цена | Особенности |
|-----|------|-------------|
| **Judge.me** | $0-$15/мес | Фото-отзывы, Google Rich Snippets |
| **Loox** | от $9.99/мес | Визуальные отзывы, виджет карусели |

### Upsell и Cross-sell

| App | Цена | Особенности |
|-----|------|-------------|
| **ReConvert** | от $4.99/мес | Post-purchase upsell ("Add transfer?") |
| **Frequently Bought Together** | $9.99/мес | "Desert Safari + Dhow Cruise = -15%" |

### WhatsApp

| App | Цена | Особенности |
|-----|------|-------------|
| **WhatsApp Chat + Abandoned Cart** | от $0 | Виджет чата, recovery |
| **SuperLemon** | от $10/мес | Уведомления заказов, cart recovery |

### Лояльность

| App | Цена | Особенности |
|-----|------|-------------|
| **Smile.io** | от $0 | Баллы за покупку, реферальная программа |
| **LoyaltyLion** | от $199/мес | Enterprise loyalty |

### Аналитика

| App | Цена | Особенности |
|-----|------|-------------|
| **Lucky Orange** | от $32/мес | Heatmaps, recordings, funnels |
| **Lifetimely** | от $19/мес | LTV, cohort analysis, ROAS |

---

## 11. Аналитика

### Shopify Analytics (встроенная)

```
Analytics -> Dashboard:
  - Total sales (AED)
  - Online store sessions
  - Conversion rate
  - Average order value
  - Top products
  - Top referrers
  - Customer geography
```

### Google Analytics 4

```
Online Store -> Preferences -> Google Analytics:
  Measurement ID: G-XXXXXXXXXX
```

Или через Shopify Custom Pixels:
```
Settings -> Customer events -> Add custom pixel:
  Name: "GA4"
  Code:
    <!-- GA4 snippet -->
```

### Facebook/Meta Pixel

```
Settings -> Customer events -> Add custom pixel:
  Name: "Meta Pixel"
  Pixel ID: 123456789
  Events: PageView, ViewContent, AddToCart, Purchase
```

### Яндекс.Метрика

```
Settings -> Customer events -> Add custom pixel:
  Name: "Yandex Metrika"
  Counter ID: 12345678
```

### Воронка для туризма

```
Session -> View Product -> Add to Cart -> Checkout -> Purchase

Типичные показатели:
  - View to Cart: 8-12%
  - Cart to Checkout: 40-55%
  - Checkout to Purchase: 60-75%
  - Overall conversion: 2-5%
```

---

## 12. Автоматизация

### Shopify Flow

**Доступен** на планах Grow ($105), Advanced ($399), Plus.

**Примеры workflow для туризма:**

**1. Новый заказ -> уведомление в Telegram:**
```
Trigger: Order created
Condition: Order total > 0
Action: Send HTTP request
  URL: https://api.telegram.org/bot{TOKEN}/sendMessage
  Method: POST
  Body: {
    "chat_id": "GROUP_CHAT_ID",
    "text": "New booking! {{ order.name }} - {{ order.total_price }} AED\n{{ order.line_items[0].title }}\nCustomer: {{ order.customer.email }}"
  }
```

**2. VIP-клиент (5+ заказов) -> тег:**
```
Trigger: Order created
Condition: Customer order count >= 5
Action: Add customer tag "VIP"
Action: Send email (loyalty bonus)
```

**3. Автоотмена неоплаченных заказов:**
```
Trigger: Order created
Condition: Payment status = pending
Wait: 24 hours
Condition: Payment status still pending
Action: Cancel order
Action: Restock inventory
```

**4. Запрос отзыва через 48ч после тура:**
```
Trigger: Order fulfilled
Wait: 48 hours
Action: Send email "How was your tour?"
  Template: review-request
  Include: Judge.me review link
```

### Zapier / Make (n8n)

Для планов без Flow (Basic):
```
Trigger: Shopify -> New Order
Action: Telegram -> Send Message
Action: Google Sheets -> Add Row
Action: WhatsApp (via Twilio) -> Send confirmation
```

### Shopify CLI

```bash
# Установка
npm install -g @shopify/cli @shopify/theme

# Работа с темой
shopify theme dev --store=myshop.myshopify.com  # Live preview
shopify theme push                                # Deploy theme
shopify theme pull                                # Download theme

# Работа с приложением
shopify app dev    # Local development
shopify app deploy # Deploy to Shopify
```

---

## 13. Практические примеры ОАЭ

### Desert Safari -- полный продукт

```json
{
  "product": {
    "title": "Desert Safari Dubai - Premium Experience",
    "body_html": "<h2>Unforgettable Desert Adventure</h2><p>Experience the thrill of dune bashing in a private 4x4 Land Cruiser, followed by a magical evening in a Bedouin camp with BBQ dinner, camel riding, henna painting, and traditional shows.</p><h3>Included:</h3><ul><li>Hotel pickup & drop-off (Dubai)</li><li>45-min dune bashing</li><li>Camel riding</li><li>Sandboarding</li><li>BBQ dinner (veg + non-veg)</li><li>Unlimited soft drinks</li><li>Tanoura & belly dance show</li><li>Henna painting</li></ul>",
    "product_type": "Tour",
    "vendor": "Dubai Tours by Suheil",
    "tags": "desert-safari, adventure, evening, pickup-included, dinner-included, dubai",
    "variants": [
      {"title": "Shared Group", "price": "180.00", "sku": "DS-SHARED-2026"},
      {"title": "Private (1-6 pax)", "price": "350.00", "sku": "DS-PRIVATE-2026"},
      {"title": "VIP + Quad Bike", "price": "550.00", "sku": "DS-VIP-QUAD-2026"}
    ],
    "metafields": [
      {"namespace": "custom", "key": "duration", "value": "6 hours", "type": "single_line_text_field"},
      {"namespace": "custom", "key": "location", "value": "Dubai Desert Conservation Reserve", "type": "single_line_text_field"},
      {"namespace": "custom", "key": "operating_hours", "value": "15:00 - 21:00", "type": "single_line_text_field"},
      {"namespace": "custom", "key": "cancellation_policy", "value": "Free cancellation 24h before", "type": "multi_line_text_field"}
    ]
  }
}
```

### Burj Khalifa -- билет с вариантами

```json
{
  "product": {
    "title": "Burj Khalifa - At The Top (124 + 125 Floor)",
    "product_type": "Ticket",
    "variants": [
      {"title": "Adult (Non-Peak)", "price": "169.00"},
      {"title": "Adult (Peak)", "price": "224.00"},
      {"title": "Adult (Sunset)", "price": "260.00"},
      {"title": "Child 4-12 (Non-Peak)", "price": "136.00"},
      {"title": "Child 0-3", "price": "0.00"}
    ]
  }
}
```

### Яхта с депозитом

```json
{
  "product": {
    "title": "Luxury Yacht Charter - 52ft Azimut (4 Hours)",
    "product_type": "Yacht",
    "variants": [
      {"title": "30% Deposit", "price": "450.00", "sku": "YC-52-DEPOSIT"},
      {"title": "Full Payment", "price": "1500.00", "sku": "YC-52-FULL"}
    ],
    "metafields": [
      {"namespace": "custom", "key": "duration", "value": "4 hours", "type": "single_line_text_field"},
      {"namespace": "custom", "key": "max_participants", "value": "12", "type": "number_integer"},
      {"namespace": "custom", "key": "includes", "value": "[\"Captain & Crew\",\"Fuel\",\"Fishing equipment\",\"Soft drinks & water\",\"Ice & cooler\"]", "type": "list.single_line_text_field"},
      {"namespace": "custom", "key": "location", "value": "Dubai Marina Yacht Club", "type": "single_line_text_field"}
    ]
  }
}
```

### Webhook -> Telegram уведомление

```javascript
const express = require('express');
const crypto = require('crypto');
const axios = require('axios');

const app = express();
app.use('/webhooks', express.raw({type: 'application/json'}));

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const SHOPIFY_WEBHOOK_SECRET = process.env.SHOPIFY_WEBHOOK_SECRET;

app.post('/webhooks/orders/create', async (req, res) => {
  // Verify webhook
  const hmac = req.headers['x-shopify-hmac-sha256'];
  const hash = crypto
    .createHmac('sha256', SHOPIFY_WEBHOOK_SECRET)
    .update(req.body)
    .digest('base64');

  if (!crypto.timingSafeEqual(Buffer.from(hmac), Buffer.from(hash))) {
    return res.status(401).send('Unauthorized');
  }

  const order = JSON.parse(req.body);

  const items = order.line_items
    .map(item => `- ${item.title} x${item.quantity} (${item.price} AED)`)
    .join('\n');

  const message = `NEW BOOKING #${order.order_number}

Customer: ${order.customer?.first_name || ''} ${order.customer?.last_name || ''}
Email: ${order.email}
Phone: ${order.phone || 'N/A'}

Items:
${items}

Total: ${order.total_price} AED
Payment: ${order.financial_status}

Notes: ${order.note || 'None'}`;

  await axios.post(
    `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`,
    { chat_id: TELEGRAM_CHAT_ID, text: message, parse_mode: 'HTML' }
  );

  res.status(200).json({received: true});
});

app.listen(3000);
```

---

## 14. Безопасность и Compliance

### PCI DSS

Shopify -- **PCI DSS Level 1** certified. Все данные карт обрабатываются на стороне Shopify. Вы никогда не видите номера карт.

### GDPR / Privacy

- Shopify автоматически показывает cookie banner (EU)
- Privacy Policy page: Settings -> Policies -> Privacy policy (шаблон включён)
- Customer data request/deletion: Settings -> Legal

### DTCM (Department of Tourism, Dubai)

Для легального туристического бизнеса в Дубае:
1. Trade License с activity "Tourism" или "Travel Agency"
2. DTCM permit для онлайн-продажи экскурсий
3. TRN (Tax Registration Number) для VAT 5%
4. Все цены должны включать VAT или чётко указывать "excl. VAT"

### Безопасность API

```javascript
// .env (добавьте в .gitignore!)
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_SECRET=your_api_secret
SHOPIFY_ACCESS_TOKEN=shpat_xxxxx
SHOPIFY_WEBHOOK_SECRET=whsec_xxxxx

// CORS -- только ваш домен
const corsOptions = {
  origin: ['https://yourdomain.com', 'https://myshop.myshopify.com'],
  methods: ['GET', 'POST'],
};
```

### Защита от мошенничества

- Включите Shopify Fraud Analysis (встроенная)
- Stripe Radar (если используете Stripe)
- Настройте Shopify Flow: автоотмена подозрительных заказов
- Мониторьте chargebacks (порог <1%)

---

## Полезные ссылки

- **Документация:** shopify.dev
- **Liquid Reference:** shopify.dev/docs/api/liquid
- **GraphQL Explorer:** shopify.dev/docs/api/admin-graphql
- **Theme Store:** themes.shopify.com
- **App Store:** apps.shopify.com
- **Shopify Community:** community.shopify.com
- **Shopify Partners:** partners.shopify.com

---

## Структура справочника

### References
- `faq.md` -- 12 частых вопросов
- `troubleshooting.md` -- 12 типичных проблем и решений
- `cheatsheet.md` -- CLI, API endpoints, Liquid, Webhooks, тарифы

---

**Версия:** 1.0
**Дата:** 13.02.2026
**Автор:** Claude Code Agent
**Для:** Туристический бизнес в ОАЭ (Сухейль)
