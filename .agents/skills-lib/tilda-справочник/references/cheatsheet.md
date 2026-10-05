# Tilda -- Шпаргалка

## Топ блоки для туризма

| Блок | Категория | Назначение |
|------|-----------|------------|
| CR400 | Cover | Первый экран с фото + CTA |
| CR300 | Cover | Видео-фон (drone footage) |
| AB300 | About | Описание тура |
| GL14 | Gallery | Фото-слайдер |
| GL100 | Gallery | Фото-сетка |
| FT300 | Features | Что входит (иконки) |
| ST200 | Store | Карточки товаров |
| ST315N | Store | Каталог из Product Catalog |
| ST100 | Store | Корзина (pop-up) |
| BF400 | Form | Полная форма заявки |
| BF200 | Form | Inline-форма |
| PR100 | Pricing | 3 тарифа колонками |
| CL100 | Reviews | Отзывы карточками |
| ME204 | Menu | Горизонтальное меню |
| ME401 | Menu | Бургер-меню (мобильное) |
| MP100 | Map | Google Maps |
| FT500 | Footer | Полный подвал |
| T123 | Other | Кастомный HTML/CSS/JS |

---

## Tilda API Endpoints

**Base URL:** `https://api.tildacdn.info`
**Rate Limit:** 150 req/hr
**Аутентификация:** publickey + secretkey (Business план)

```
GET /v1/getprojectslist     -- список проектов
GET /v1/getprojectinfo      -- детали проекта (+ projectid)
GET /v1/getpageslist        -- список страниц (+ projectid)
GET /v1/getpage             -- body HTML (+ pageid)
GET /v1/getpagefull         -- полный HTML (+ pageid)
GET /v1/getpageexport       -- экспорт body (+ pageid)
GET /v1/getpagefullexport   -- полный экспорт (+ pageid)
```

**Пример:**
```
https://api.tildacdn.info/v1/getpageslist/?publickey=KEY&secretkey=SECRET&projectid=12345
```

**Ответ:** `{"status": "FOUND", "result": [...]}`

---

## Webhook формат (форма -> ваш сервер)

**Метод:** POST
**Content-Type:** application/x-www-form-urlencoded

**Поля:**
```
Name=Иван
Phone=+79991234567
Email=ivan@mail.com
tour=Desert Safari
date=2026-03-15
guests=4
tranid=12345678       # Уникальный Lead ID
formid=987654         # ID блока формы
```

**Настройка:** Site Settings -> Forms -> Webhook -> URL

---

## CSS хаки

```css
/* Скруглить кнопки */
.t-btn { border-radius: 30px !important; }

/* Цвет CTA */
.t-btn_md {
  background-color: #e67e22 !important;
  border-color: #e67e22 !important;
}

/* Скрыть блок на мобильном */
@media (max-width: 640px) {
  #rec123456789 { display: none; }
}

/* Кастомный шрифт */
.t-title { font-family: 'Montserrat', sans-serif !important; }

/* Стилизация конкретного блока */
#rec123456789 .t-card__title { color: #2c3e50; }

/* Sticky header */
.t-cover { position: sticky; top: 0; z-index: 100; }

/* RTL для арабского */
body { direction: rtl; }
.t-text { text-align: right; }
```

---

## JS паттерны

```javascript
// Ожидание загрузки Tilda
t_onReady(function() {
  console.log('Tilda ready');
});

// Событие формы
document.querySelector('.js-form-proccess').addEventListener(
  'tildaform:aftersuccess', function(e) {
    var form = e.target;
    var leadId = form.tildaTranId;
    // GA4 event
    gtag('event', 'generate_lead', { value: 180, currency: 'AED' });
    // Redirect
    window.location.href = '/thank-you';
  }
);

// Клик по CTA -> Яндекс.Метрика
t_onReady(function() {
  document.querySelectorAll('.t-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      ym(12345678, 'reachGoal', 'cta_click');
    });
  });
});

// jQuery (доступен глобально)
$(document).ready(function() {
  $("[href='#rec123456789']").click(function() {
    // обработка клика
  });
});
```

---

## SEO чеклист

| Элемент | Где настроить | Пример |
|---------|--------------|--------|
| Title | Page Settings | "Desert Safari Dubai - from 180 AED" |
| Description | Page Settings | 150-160 символов, с ключевыми словами |
| H1 | Блок Cover/Title | 1 на страницу, главный заголовок |
| Alt-теги | Content Panel изображения | "Desert safari sunset Dubai" |
| URL alias | Page Settings | `/desert-safari` (не `/page12345`) |
| OG image | Page Settings -> OG | 1200x630, фото + лого + цена |
| HTTPS | Site Settings -> SEO | Включить переключателем |
| Sitemap | Автоматически | `yourdomain.com/sitemap.xml` |
| Robots.txt | Автоматически | Генерируется Tilda |
| Schema.org | Page Settings -> HEAD | JSON-LD код (TouristTrip) |
| hreflang | Page Settings -> HEAD | Для мультиязычных страниц |
| Favicon | Site Settings -> SEO | .ico или .png |

---

## Тарифы (2026)

| | Free | Personal | Business |
|--|------|----------|----------|
| **Цена** | $0 | $15/мес | $25/мес |
| **Сайтов** | 1 | 1 | 5 |
| **Страниц** | 50 | 500 | 500/сайт |
| **Домен** | .tilda.ws | Свой | Свой |
| **Все блоки** | Нет | Да | Да |
| **Магазин** | Нет | Да | Да |
| **Формы** | Базовые | Полные | Полные |
| **API** | Нет | Нет | Да |
| **Экспорт** | Нет | Нет | Да |
| **Хранилище** | 50 МБ | 1 ГБ | 1 ГБ |
| **HTML in HEAD** | Нет | Страница | Сайт + Страница |

---

## Приёмники форм

| Сервис | Настройка |
|--------|-----------|
| Email | Site Settings -> Forms -> Email |
| Google Sheets | Forms -> Google -> авторизация |
| Telegram | Forms -> Telegram -> Token + Chat ID |
| Webhook | Forms -> Webhook -> HTTPS URL |
| AmoCRM | Forms -> AmoCRM -> авторизация |
| Bitrix24 | Forms -> Bitrix24 -> URL портала |
| MailChimp | Forms -> MailChimp -> API Key |
| Slack | Forms -> Slack -> Webhook URL |
| Salesforce | Forms -> Salesforce |
| HubSpot | Forms -> HubSpot |
| UniSender | Forms -> UniSender |
| GetResponse | Forms -> GetResponse |

---

## WhatsApp CTA ссылка

```
https://wa.me/971XXXXXXXXX?text=Здравствуйте!%20Хочу%20забронировать%20Desert%20Safari
```

Замените `971XXXXXXXXX` на номер без `+`. URL-encode текст.

---

## Полезные ссылки

| Ресурс | URL |
|--------|-----|
| Справочный центр | help.tilda.cc |
| Обучение | tilda.education |
| Zero Block | zero.tilda.cc |
| Шаблоны | tilda.cc/tpls |
| API | help.tilda.cc/api |
| Тарифы | tilda.cc/pricing |
| Блог | blog-en.tilda.cc |
| Webhook тест | webhook.site |
