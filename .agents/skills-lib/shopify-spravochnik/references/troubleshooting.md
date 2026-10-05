# Shopify для туризма ОАЭ -- Troubleshooting (12 проблем)

---

## 1. Shopify Payments недоступен в ОАЭ

**Симптом:** Settings -> Payments -> "Shopify Payments isn't available in your country"

**Причина:** ОАЭ не в списке 23 поддерживаемых стран Shopify Payments.

**Решение:**
1. Settings -> Payments -> Third-party providers
2. Выберите один из доступных: Stripe, Telr, PayTabs, Checkout.com
3. Зарегистрируйтесь у провайдера, получите API keys
4. Введите credentials в Shopify
5. Протестируйте в test mode

**Важно:** без Shopify Payments взимается доп. комиссия: 2% (Basic), 1% (Grow), 0.6% (Advanced) сверх комиссии провайдера.

---

## 2. Liquid ошибки: "undefined method" или пустые metafields

**Симптом:** `{{ product.metafields.custom.duration }}` выводит пустоту или ошибку.

**Причины и решения:**

**a) Metafield не создан:**
```
Settings -> Custom data -> Products -> Add definition
  Namespace: custom
  Key: duration
  Type: Single line text
```

**b) Metafield создан, но не заполнен для конкретного продукта:**
- Откройте продукт -> прокрутите вниз -> заполните metafield

**c) Неправильный путь доступа:**
```liquid
<!-- WRONG -->
{{ product.metafield.custom.duration }}

<!-- CORRECT -->
{{ product.metafields.custom.duration }}
<!-- Или через .value для JSON типов -->
{{ product.metafields.custom.duration.value }}
```

**d) Metafield type = list:**
```liquid
<!-- Для list типов используйте .value и цикл -->
{% for item in product.metafields.custom.includes.value %}
  {{ item }}
{% endfor %}
```

---

## 3. Валюта отображается неправильно (USD вместо AED)

**Симптом:** Цены показываются в долларах или без символа валюты.

**Решение:**
1. Settings -> Store details -> Store currency: **AED** (United Arab Emirates Dirham)
2. Settings -> Markets -> Primary market -> United Arab Emirates -> Currency: AED
3. Убедитесь что в Liquid используете правильный фильтр:
```liquid
{{ product.price | money }}              <!-- 350.00 AED -->
{{ product.price | money_with_currency }} <!-- 350.00 AED -->
```

**Для мульти-валюты:**
```liquid
{{ product.price | money }}
<!-- Автоматически отображает в валюте текущего Market -->
```

---

## 4. Webhook не приходит или отклоняется

**Симптом:** Shopify показывает webhook как failed, сервер не получает запросы.

**Причины и решения:**

**a) URL недоступен:**
- Webhook URL должен быть HTTPS с валидным SSL
- Для локальной разработки используйте ngrok: `ngrok http 3000`

**b) Сервер возвращает не 200:**
```javascript
// Обязательно возвращайте 200 быстро
app.post('/webhooks/orders', async (req, res) => {
  res.status(200).json({received: true}); // Сначала ответ!
  // Потом обработка асинхронно
  processOrder(req.body).catch(console.error);
});
```

**c) Verification failure:**
```javascript
// Обязательно используйте raw body для HMAC
app.use('/webhooks', express.raw({type: 'application/json'}));
// НЕ express.json() для webhook endpoint!
```

**d) Webhook удалён:**
- Проверьте: Settings -> Notifications -> Webhooks
- Или через API: `GET /admin/api/2025-01/webhooks.json`

**Shopify ретраит webhook** 19 раз в течение 48 часов. После этого webhook автоматически удаляется.

---

## 5. Rate Limit ошибки (429 Too Many Requests)

**Симптом:** `HTTP 429 Too Many Requests` при API-запросах.

**REST API:**
```javascript
// Проверяйте заголовок
const callLimit = response.headers['x-shopify-shop-api-call-limit'];
// "32/40" -> 32 использовано из 40

// Решение: throttling
async function shopifyRequest(url) {
  const response = await fetch(url, {headers});
  if (response.status === 429) {
    const retryAfter = response.headers['retry-after'] || 2;
    await sleep(retryAfter * 1000);
    return shopifyRequest(url); // retry
  }
  return response;
}
```

**GraphQL API:**
```javascript
// Проверяйте cost в ответе
// "throttleStatus": {"currentlyAvailable": 950, "maximumAvailable": 1000}
// Если currentlyAvailable < 100, подождите
```

**Best practices:**
- Используйте Bulk Operations для массовых запросов (GraphQL)
- Кэшируйте ответы (products меняются редко)
- Используйте webhooks вместо polling

---

## 6. Мультиязычность: переводы не отображаются

**Симптом:** Переключатель языка работает, но контент остаётся на английском.

**Решение:**

**a) Проверьте что языки опубликованы:**
```
Settings -> Languages -> Убедитесь что RU и AR имеют статус "Published"
```

**b) Переведите контент:**
- Откройте Translate & Adapt app
- Выберите язык (Russian)
- Переведите: Products, Collections, Theme strings
- **Каждый продукт** нужно перевести отдельно

**c) Тема поддерживает мультиязычность:**
```
Online Store -> Themes -> тема должна использовать {{ | t }} фильтр
```

**d) URL-переключатель:**
```liquid
{% for locale in shop.published_locales %}
  <a href="{{ locale.root_url }}{{ request.path }}">
    {{ locale.endonym_name }}
  </a>
{% endfor %}
```

---

## 7. Metafields не появляются на странице продукта

**Симптом:** Metafields заполнены в admin, но не видны на витрине.

**Решение:**

**Способ 1: Dynamic sources (рекомендуемый для Online Store 2.0)**
1. Customize theme -> Product page
2. Добавьте блок "Custom Liquid"
3. В настройках блока -> "Connect dynamic source" -> выберите metafield

**Способ 2: Код в секции**
```liquid
{% if product.metafields.custom.duration %}
  <div class="tour-duration">
    Duration: {{ product.metafields.custom.duration.value }}
  </div>
{% endif %}
```

**Способ 3: Добавьте metafield в section schema**
```json
{
  "settings": [
    {
      "type": "text",
      "id": "metafield_key",
      "label": "Metafield key",
      "default": "custom.duration"
    }
  ]
}
```

---

## 8. Скорость загрузки низкая (PageSpeed < 50)

**Симптом:** Google PageSpeed Insights показывает низкий балл, медленная загрузка.

**Причины и решения:**

**a) Слишком много apps:**
- Каждое app добавляет JS/CSS
- Удалите неиспользуемые: Apps -> Remove unused
- Проверьте: View page source -> найдите `<script>` от apps

**b) Большие изображения:**
```liquid
<!-- Используйте Shopify Image CDN с параметрами -->
{{ product.featured_image | image_url: width: 800 }}
<!-- Shopify автоматически конвертирует в WebP -->

<!-- Lazy loading для изображений ниже fold -->
<img src="{{ image | image_url: width: 600 }}" loading="lazy" alt="{{ image.alt }}">
```

**c) Неоптимизированная тема:**
- Используйте Dawn (бесплатная, самая быстрая)
- Или проверьте theme speed: Online Store -> Themes -> Speed score

**d) Много внешних скриптов:**
- GA4, Meta Pixel, Яндекс.Метрика -- загружайте async
- Используйте Shopify Custom Pixels (загружаются в web worker)

---

## 9. RTL (арабский) отображается некорректно

**Симптом:** Арабский текст показывается слева направо, layout ломается.

**Решение:**

**a) Тема поддерживает RTL?**
- Dawn и большинство Shopify 2.0 тем поддерживают RTL
- Проверьте: `theme.liquid` должен содержать `dir="{{ direction }}"`

**b) Добавьте RTL в theme.liquid:**
```liquid
<html lang="{{ request.locale.iso_code }}"
      dir="{% if request.locale.iso_code == 'ar' %}rtl{% else %}ltr{% endif %}">
```

**c) CSS фиксы:**
```css
[dir="rtl"] { text-align: right; }
[dir="rtl"] .flex-row { flex-direction: row-reverse; }
[dir="rtl"] .ml-auto { margin-left: 0; margin-right: auto; }
[dir="rtl"] .breadcrumb-separator { transform: scaleX(-1); }
```

---

## 10. Корзина: клиент не может завершить checkout

**Симптом:** Клиент добавляет в корзину, но checkout не загружается или выдаёт ошибку.

**Причины и решения:**

**a) Платёжный шлюз не настроен:**
```
Settings -> Payments -> Убедитесь что есть активный провайдер
```

**b) Валюта не поддерживается провайдером:**
- Проверьте что AED поддерживается вашим gateway
- Stripe: да. Telr: да. PayPal: да.

**c) Shipping не настроен для "цифровых" продуктов:**
```
Settings -> Shipping -> Zones -> Убедитесь что нет обязательной доставки
Или: Product -> Uncheck "This is a physical product"
```

**d) CORS / Mixed content:**
- Если используете custom domain, проверьте что SSL валидный
- Все ресурсы должны загружаться по HTTPS

**e) App конфликт:**
- Отключите apps по одному для диагностики
- Частый конфликт: несколько cart/checkout apps одновременно

---

## 11. Booking app: календарь не появляется на странице продукта

**Симптом:** BookThatApp или Sesami установлен, но виджет календаря не виден.

**Решение:**

**BookThatApp:**
1. Откройте продукт в admin -> BookThatApp tab -> Enable booking
2. Настройте availability (дни, time slots)
3. Theme -> Customize -> Product page -> убедитесь что app block добавлен

**Sesami:**
1. Sesami Dashboard -> Products -> Connect product
2. Services -> создайте service с duration
3. Theme -> Customize -> Product page -> Add block -> Sesami widget

**Общие проблемы:**
- App embed не включён: Online Store -> Themes -> Customize -> App embeds -> Toggle ON
- Конфликт с другим app (отключите по одному)
- JavaScript ошибка в консоли (F12 -> Console)

---

## 12. Fulfillment: как отправить email-ваучер вместо посылки

**Симптом:** Shopify ожидает tracking number для fulfillment.

**Решение:**

**a) Автоматический fulfill для digital products:**
```
Settings -> Checkout -> Order processing -> After an order has been paid:
  Select: "Automatically fulfill the order's line items"
```

**b) Custom email notification:**
```
Settings -> Notifications -> Order confirmation -> Customize template
  Добавьте: ваучер, QR-код, инструкции
```

**c) Через App:**
- **Digital Downloads** (бесплатный от Shopify) -- прикрепляет файл к продукту
- Используйте для PDF-ваучеров с QR-кодом

**d) Через API (webhook):**
```javascript
// При fulfillment отправьте PDF-ваучер
app.post('/webhooks/orders/paid', async (req, res) => {
  const order = JSON.parse(req.body);
  const voucher = await generateVoucherPDF(order);
  await sendVoucherEmail(order.email, voucher);
  // Mark as fulfilled
  await shopify.graphql(`
    mutation {
      fulfillmentCreateV2(fulfillment: {
        lineItemsByFulfillmentOrder: [{
          fulfillmentOrderId: "${fulfillmentOrderId}"
        }]
        trackingInfo: { number: "VOUCHER-${order.order_number}" }
      }) {
        fulfillment { id }
      }
    }
  `);
  res.sendStatus(200);
});
```
