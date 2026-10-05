# Shopify для туризма ОАЭ -- FAQ (12 вопросов)

---

## 1. Можно ли продавать услуги (экскурсии, туры) на Shopify?

**Да.** Shopify поддерживает продажу услуг, несмотря на то что изначально создан для физических товаров. Ключевые настройки:

- **Снимите галочку** "This is a physical product" -- отключает доставку
- **Используйте variants** для типов (Shared/Private/VIP) и дат
- **Установите booking app** (BookThatApp, Sesami) для выбора даты/времени
- **Metafields** для информации: длительность, маршрут, что включено
- **Digital fulfillment** -- отправка email-ваучера вместо физической доставки

Тысячи туроператоров успешно используют Shopify для продажи экскурсий, билетов и аренды.

---

## 2. Какой тариф выбрать для туристического бизнеса в Дубае?

**Рекомендация по стадиям:**

| Стадия | Тариф | Цена | Почему |
|--------|-------|------|--------|
| Старт/тест | Basic | $39/мес | Полный магазин, 2 сотрудника, достаточно для начала |
| Рост (>$10K/мес) | Grow | $105/мес | Shopify Flow (автоматизация), лучшие отчёты, 5 сотрудников |
| Масштаб | Advanced | $399/мес | Расширенные отчёты, лучшие ставки на комиссии |
| Офлайн-офис | + Retail | $89/мес | POS-терминал для приёма оплат в офисе (Tecom) |

Есть скидка 25% при годовой оплате: Basic $29/мес, Grow $79/мес.

**Starter ($5/мес)** подходит только для продажи через ссылки в WhatsApp/Instagram без полноценного магазина.

---

## 3. Работает ли Shopify Payments в ОАЭ?

**Нет** (на февраль 2026). Shopify Payments доступен в 23 странах, но ОАЭ не в списке.

**Альтернативы:**
- **Stripe** -- лучший для международных карт, 135+ валют, мгновенная интеграция
- **Telr** -- лучший для локальных карт ОАЭ (Emirates NBD, ADCB), AED-first
- **PayTabs** -- хорошая fraud prevention, арабский интерфейс
- **Amazon Payment Services** (бывший PayFort) -- доверие местного рынка
- **Checkout.com** -- для высокого оборота (индивидуальные ставки)

Все подключаются через Settings -> Payments -> Add payment methods.

**Важно:** без Shopify Payments применяется дополнительная комиссия 2% на каждую транзакцию (Basic), 1% (Grow), 0.6% (Advanced). Это сверх комиссии платёжного шлюза.

---

## 4. Как настроить выбор даты/времени тура?

Shopify не имеет встроенного календаря. Используйте приложения:

**BookThatApp** ($15/мес):
1. Install из App Store
2. Перейдите на продукт -> BookThatApp -> Configure
3. Задайте доступные дни и time slots (например, Desert Safari: ежедневно 15:00-15:30 pickup)
4. Установите capacity (макс. участников на слот)
5. Календарь автоматически появится на странице продукта

**Sesami** (Free plan доступен):
1. Install -> Connect products
2. Настройте Services с duration и buffer time
3. Настройте Staff availability
4. Sync с Google Calendar

**Результат:** клиент выбирает дату в календаре -> вариант автоматически создаётся -> заказ содержит дату/время.

---

## 5. Как сделать магазин на 3 языках (RU/EN/AR)?

**Шаг 1: Включите Markets**
```
Settings -> Markets -> Add market -> Выберите страны для каждого языка
```

**Шаг 2: Добавьте языки**
```
Settings -> Languages -> Add language -> Russian, Arabic
```

**Шаг 3: Переведите контент**
- Установите бесплатное приложение **Shopify Translate & Adapt**
- Переведите: продукты, коллекции, страницы, навигацию, тему
- Или загрузите переводы через CSV

**Шаг 4: Арабский (RTL)**
- Используйте тему с поддержкой RTL (Dawn поддерживает)
- Проверьте CSS для RTL-направления текста

**URL-структура:**
```
EN: /products/desert-safari
RU: /ru/products/desert-safari
AR: /ar/products/desert-safari
```

Shopify автоматически генерирует hreflang-теги для SEO.

---

## 6. Как настроить депозит (частичную оплату)?

**Способ 1: Варианты продукта**
```
Variants:
  "30% Deposit" -> 450 AED (для яхты 1500 AED)
  "Full Payment" -> 1500 AED
```
В описании укажите: "Остаток оплачивается за 48ч до мероприятия".

**Способ 2: Apps**
- **Deposit & Partial Payments** (Shopify App Store) -- автоматически считает процент
- **Partially** -- гибкие депозиты, напоминания об остатке

**Способ 3: Draft Orders (вручную)**
```
Orders -> Create order -> Add items -> Apply deposit discount
-> Send invoice to customer (email/WhatsApp)
-> Create second invoice for balance later
```

---

## 7. Как принимать оплату в RUB/KZT?

**Автоматическая конвертация (Markets):**
```
Settings -> Markets -> Russia -> Currency: USD (RUB не поддерживается Stripe)
```

**Manual Payment (для Kaspi/Сбер):**
```
Settings -> Payments -> Manual payment methods -> Create custom:
  Name: "Перевод на карту (Сбер/Kaspi)"
  Instructions:
    "Сбер: 1234 5678 9012 3456
     Kaspi: +7 777 123 4567
     В комментарии: номер заказа
     Отправьте скриншот в WhatsApp: +971501234567"
```

Клиент выбирает этот метод при checkout -> получает инструкции -> переводит -> присылает чек -> вы подтверждаете вручную.

**Криптовалюта:**
Установите NOWPayments или Coinbase Commerce -> клиент платит USDT/BTC -> автоматическая конвертация.

---

## 8. Как интегрировать с Telegram/WhatsApp ботом?

**Telegram (через Webhook):**
1. Shopify Flow или webhook на `ORDERS_CREATE`
2. Сервер получает заказ -> отправляет в Telegram Bot API
3. Бот уведомляет в группу/канал: "Новый заказ #1234, Desert Safari, 350 AED"

**WhatsApp (через App):**
- **SuperLemon** -- отправляет уведомления о заказах через WhatsApp Business API
- **WhatsApp Chat Widget** -- кнопка чата на сайте

**WhatsApp (через Webhook + Twilio):**
```javascript
// Webhook handler
app.post('/webhooks/orders', async (req, res) => {
  const order = JSON.parse(req.body);
  await twilio.messages.create({
    from: 'whatsapp:+14155238886',
    to: `whatsapp:${order.customer.phone}`,
    body: `Booking confirmed! #${order.order_number}\n${order.line_items[0].title}\nTotal: ${order.total_price} AED`
  });
  res.sendStatus(200);
});
```

---

## 9. Какие Apps обязательны для туристического магазина?

**Критические (must-have):**
1. **Booking app** (BookThatApp / Sesami) -- выбор даты
2. **Judge.me** (бесплатный) -- отзывы с фото, Google Rich Snippets
3. **Shopify Translate & Adapt** (бесплатный) -- мультиязычность

**Рекомендуемые:**
4. **WhatsApp Chat** -- кнопка связи на каждой странице
5. **ReConvert** -- upsell после покупки ("Add hotel transfer?")
6. **Smile.io** (бесплатный tier) -- программа лояльности

**По необходимости:**
7. **Lucky Orange** -- heatmaps, записи сессий
8. **NOWPayments** -- криптовалюта
9. **Matrixify** -- массовый импорт/экспорт (Excel/CSV)

**Важно:** каждое приложение добавляет JS-код и замедляет сайт. Устанавливайте только то, что реально используете.

---

## 10. Как настроить Schema.org для экскурсий?

Добавьте JSON-LD разметку в тему:

1. Online Store -> Themes -> Edit code
2. Откройте `snippets/` -> Add snippet -> `schema-tour.liquid`
3. Добавьте JSON-LD с типами `TouristTrip` + `Product`:

```liquid
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": ["TouristTrip", "Product"],
  "name": {{ product.title | json }},
  "description": {{ product.description | strip_html | truncate: 500 | json }},
  "image": {{ product.featured_image | image_url: width: 1200 | json }},
  "offers": {
    "@type": "AggregateOffer",
    "priceCurrency": "AED",
    "lowPrice": {{ product.price_min | money_without_currency | json }},
    "highPrice": {{ product.price_max | money_without_currency | json }},
    "availability": "https://schema.org/InStock"
  }
}
</script>
```

4. Включите snippet в `templates/product.liquid` или в section:
```liquid
{% render 'schema-tour' %}
```

5. Проверьте через Google Rich Results Test.

---

## 11. REST API vs GraphQL -- что выбрать?

**GraphQL** -- однозначно для новых проектов.

| Критерий | REST (legacy) | GraphQL |
|---------|---------------|---------|
| **Статус** | Legacy с октября 2024 | Рекомендуемый |
| **Новые apps** | Запрещён для public apps (с апреля 2025) | Обязательный |
| **Rate limits** | 40 req/мин (2 req/сек) | 1000 cost points (50/сек) |
| **Гибкость** | Фиксированные поля | Запрашиваете только нужные поля |
| **Связанные данные** | Несколько запросов | Один запрос с connections |
| **Документация** | Полная | Полная + GraphiQL explorer |

**Когда REST ещё OK:**
- Простая custom app для своего магазина
- Быстрый скрипт для одноразового импорта
- Существующая интеграция, которая работает

**Всегда GraphQL:**
- Новое приложение для App Store
- Интеграция с CRM/ERP
- Мобильное приложение или headless storefront

---

## 12. Как импортировать каталог из Google Sheets/Notion?

**Способ 1: CSV (встроенный)**
1. Подготовьте CSV с колонками: Handle, Title, Body (HTML), Vendor, Type, Tags, Variant Price, Image Src
2. Products -> Import -> Upload CSV
3. Shopify создаст все продукты

**Способ 2: Matrixify (Excel/Google Sheets)**
1. Установите Matrixify (бесплатно до 10 товаров)
2. Экспортируйте шаблон Excel
3. Заполните в Google Sheets
4. Импортируйте обратно (products, metafields, images)

**Способ 3: API + скрипт**
```javascript
const products = await fetchFromGoogleSheets(SHEET_ID);

for (const product of products) {
  await shopify.graphql(`
    mutation {
      productCreate(input: {
        title: "${product.title}"
        descriptionHtml: "${product.description}"
        productType: "${product.type}"
        variants: [{ price: "${product.price}" }]
      }) {
        product { id }
        userErrors { field message }
      }
    }
  `);
}
```

**Способ 4: Notion -> Shopify (через Zapier/Make)**
```
Trigger: New item in Notion database
Action: Create Product in Shopify
  Map fields: Title, Description, Price, Tags
```
