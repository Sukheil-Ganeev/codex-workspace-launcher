---
name: tilda-справочник
description: "Production-ready руководство по Tilda для создания лендингов и каталогов туристического бизнеса ОАЭ. Zero Code блоки, кастомный HTML/CSS/JS, Tilda API (лиды, страницы), интеграция с CRM (Notion, AmoCRM), мессенджерами (Telegram, WhatsApp), платёжными системами, SEO, мультиязычные сайты. Используй когда нужно создать или настроить сайт/лендинг на Tilda для туристических услуг."
---
# Tilda -- Лендинги и каталоги для туристического бизнеса ОАЭ

## 1. Обзор платформы и выбор тарифа

### Что такое Tilda

Tilda Publishing -- визуальный конструктор сайтов на блоках. Позволяет собирать лендинги, многостраничные сайты и интернет-магазины без кода. 550+ готовых блоков, Zero Block (дизайн-редактор), встроенный магазин, CRM, аналитика.

### Тарифы (2026)

| Тариф | Цена | Сайтов | Страниц | Ключевые возможности |
|-------|------|--------|---------|---------------------|
| **Free** | $0 | 1 | 50 | Базовые блоки, поддомен tilda.ws, 50 МБ хранилище |
| **Personal** | $15/мес | 1 | 500 | Все блоки, свой домен, SSL, формы, магазин, аналитика, 1 ГБ |
| **Business** | $25/мес | 5 | 500/сайт | Всё из Personal + экспорт кода, API, 5 сайтов, HTML-блок в шапке |

**Рекомендация для туристического бизнеса:** Personal для одного лендинга/каталога. Business если нужно несколько сайтов (экскурсии + яхты + авто) или API.

### Tilda vs Shopify vs WordPress

| Критерий | Tilda | Shopify | WordPress |
|----------|-------|---------|-----------|
| **Лендинги** | Отлично | Слабо | Хорошо (Elementor) |
| **E-commerce** | Базовый магазин | Полноценный | WooCommerce |
| **Скорость запуска** | 2-4 часа | 1-2 дня | 2-5 дней |
| **Код** | Не нужен | Liquid шаблоны | PHP/темы |
| **Стоимость** | $15-25/мес | $29-299/мес | $5-30/мес хостинг |
| **Для кого** | Лендинги, каталоги, портфолио | Полноценные магазины | Блоги, сложные сайты |

**Когда Tilda:** лендинг экскурсии, каталог туров, визитка бизнеса, мультиязычный сайт.
**Когда Shopify:** полноценный онлайн-магазин с инвентарём, скидками, подписками.

---

## 2. Быстрый старт: лендинг за 2 часа

### Пошаговый план

1. **Регистрация:** tilda.cc -> Create Free Account
2. **Создать проект:** Dashboard -> Create New Site -> Blank Site
3. **Создать страницу:** Create New Page -> выбрать шаблон или пустую
4. **Собрать из блоков:**
   - Cover (CR) -- первый экран с заголовком и CTA
   - About (AB) -- описание тура
   - Gallery (GL) -- фотографии
   - Features (FT) -- что входит в тур
   - Pricing (PR) -- цены
   - Form (BF) -- форма заявки
   - Footer (FT) -- контакты и соцсети

5. **Настроить форму:** Site Settings -> Forms -> добавить приёмник (Email/Telegram)
6. **Подключить домен:** Site Settings -> Domain (Personal/Business план)
7. **Опубликовать:** кнопка Publish

### Структура лендинга "Desert Safari"

```
[Cover CR400]     -- "Незабываемое сафари в пустыне Дубая" + фото + CTA "Забронировать"
[About AB300]     -- Описание тура: джипы, верблюды, BBQ, шоу
[Gallery GL100]   -- 6-8 фото пустыни, закат, лагерь
[Steps ST200]     -- Как это работает: 1. Заявка 2. Оплата 3. Трансфер
[Features FT300]  -- Что входит: транспорт, ужин, шоу, фото
[Pricing PR100]   -- Тарифы: Standard 180 AED, VIP 350 AED, Private 1200 AED
[Reviews CL100]   -- Отзывы клиентов (3-4 карточки)
[Form BF400]      -- Имя, телефон, дата, кол-во гостей
[Map MP100]       -- Карта точки сбора
[Footer FT500]    -- Контакты, WhatsApp, Instagram, Telegram
```

---

## 3. Zero Code блоки -- каталог для туризма

### Категории блоков

| Категория | Префикс | Назначение | Топ блоки для туризма |
|-----------|---------|------------|----------------------|
| **Cover** | CR | Первый экран | CR400 (фото + текст + CTA), CR300 (видео-фон) |
| **About** | AB | О компании/туре | AB300, AB400 |
| **Features** | FT | Что входит в тур | FT300 (иконки + текст), FT200 |
| **Gallery** | GL | Фото экскурсий | GL100 (сетка), GL14 (слайдер), GL200 (pop-up) |
| **Store** | ST | Каталог/магазин | ST200 (карточки), ST315N (каталог), ST100 (корзина) |
| **Form** | BF | Формы заявок | BF400 (полная), BF200 (inline), BF600N (с фоном) |
| **Pricing** | PR | Тарифы/цены | PR100 (колонки), PR200 (таблица) |
| **Team** | TM | Команда/гиды | TM200, TM300 |
| **Timeline** | TL | Расписание/этапы | TL100, TL200 |
| **Tabs** | TX | Вкладки контента | TX200, TX300 |
| **Reviews** | CL | Отзывы клиентов | CL100 (карточки), CL200 (слайдер) |
| **Footer** | FT | Подвал страницы | FT500 (полный), FT300 |
| **Menu** | ME | Навигация | ME204 (горизонт.), ME401 (бургер) |
| **Map** | MP | Карта | MP100 (Google Maps) |
| **Pop-up** | ST | Всплывающие окна | ST100 (корзина), Pop-up формы |
| **Feeds** | FD | Блог/лента | FD302 (карточки статей) |

### Zero Block -- кастомный дизайн

Zero Block -- встроенный визуальный редактор для создания уникальных блоков. Позволяет размещать элементы с точностью до пикселя.

**Возможности:**
- Свободное размещение текста, изображений, кнопок, фигур
- Анимации (появление, параллакс, hover)
- Адаптивность (настройка для каждого breakpoint: 1200, 960, 640, 480, 320)
- Видео-фон, наложение градиентов
- Grid-привязка (12-колоночная сетка)

**Когда использовать:** уникальный первый экран, нестандартная карточка тура, промо-баннер со сложной анимацией.

---

## 4. Каталог и карточки продуктов (Tilda Store)

### Настройка магазина

1. **Подключить платёжную систему:** Site Settings -> Payment Systems -> Stripe/PayPal
2. **Добавить товары:** Site Settings -> Shopping Cart -> Products -> Add Product
3. **Создать каталог:** добавить блок ST315N (Product Catalog) на страницу
4. **Настроить корзину:** блок ST100 (Shopping Cart) -- pop-up или отдельная страница

### Карточка товара-экскурсии

```
Название: Desert Safari VIP
Описание: Приватный джип, ужин BBQ, верблюды, шоу
Цена: 350 AED
Изображение: desert_safari_vip.jpg
Опции:
  - Дата: [выбор даты]
  - Гости: 1 / 2 / 3 / 4+
  - Трансфер: Да (+50 AED) / Нет
Характеристики:
  - Длительность: 6 часов
  - Время: 15:00 - 21:00
  - Язык: RU / EN
```

### Особенности Tilda Store

| Функция | Поддержка |
|---------|-----------|
| Карточки товаров | До 5000 товаров |
| Варианты (размеры, цвета) | До 30 вариантов |
| Фильтры и поиск | Встроенные |
| Корзина | Pop-up или страница |
| Промокоды | Встроенные |
| Автоматический расчёт | Сумма, кол-во |
| Экспорт/импорт CSV | Массовое добавление |
| Складской учёт | Базовый (кол-во) |

### Для туризма

- Каждая экскурсия = товар с ценой в AED
- Опция "Дата" через текстовое поле или выбор
- Групповые скидки через промокоды
- Связка с формой для сложных заказов (яхты, VIP-программы)

---

## 5. Формы и сбор лидов

### Встроенные приёмники данных

Tilda поддерживает 12+ приёмников форм:

| Сервис | Настройка |
|--------|-----------|
| **Email** | Site Settings -> Forms -> Email -> ввести адрес -> подтвердить |
| **Google Sheets** | Site Settings -> Forms -> Google -> авторизация -> выбрать таблицу |
| **Telegram** | Site Settings -> Forms -> Telegram -> вставить Bot Token + Chat ID |
| **Webhook** | Site Settings -> Forms -> Webhook -> URL вашего скрипта |
| **AmoCRM** | Site Settings -> Forms -> AmoCRM -> авторизация |
| **Bitrix24** | Site Settings -> Forms -> Bitrix24 -> URL портала |
| **MailChimp** | Site Settings -> Forms -> MailChimp -> API Key |
| **Slack** | Site Settings -> Forms -> Slack -> Webhook URL |
| **Salesforce** | Site Settings -> Forms -> Salesforce -> авторизация |
| **HubSpot** | Site Settings -> Forms -> HubSpot -> авторизация |
| **UniSender** | Site Settings -> Forms -> UniSender -> API Key |
| **GetResponse** | Site Settings -> Forms -> GetResponse -> API Key |

### Настройка Telegram бота для лидов

**Шаг 1:** Написать @TildaFormsBot в Telegram -> нажать "Start" -> получить API Key и Secret Key
**Шаг 2:** Site Settings -> Forms -> Telegram -> вставить полученные API Key и Secret Key
**Шаг 3:** Подтвердить или пропустить шаг "Assign service to all forms"
**Шаг 4:** Если пропустили -- в редакторе страницы открыть блок формы -> Content -> выбрать Telegram как приёмник
**Шаг 5:** Опубликовать страницу

**Для группы:** добавить @TildaFormsBot в группу через Add Members -> написать /start в чате группы -> следовать инструкциям. API Key для групп может быть отрицательным (с минусом).

**Результат:** при отправке формы бот мгновенно шлёт сообщение в чат:
```
Новая заявка!
Имя: Иван
Телефон: +7 999 123 4567
Экскурсия: Desert Safari
Дата: 15.03.2026
Гости: 4
```

### Webhook формат

При отправке формы Tilda шлёт POST-запрос на указанный URL:

```json
{
  "Name": "Иван",
  "Phone": "+79991234567",
  "Email": "ivan@mail.com",
  "tour": "Desert Safari",
  "date": "2026-03-15",
  "guests": "4",
  "tranid": "12345678",
  "formid": "987654"
}
```

**Метаданные:**
- `tranid` -- уникальный ID лида (из CRM Tilda)
- `formid` -- ID блока формы на странице

**Cookies (опционально):** UTM-метки, источник трафика.

**Пример Node.js приёмника:**
```javascript
const express = require('express');
const app = express();
app.use(express.urlencoded({ extended: true }));

app.post('/tilda-webhook', (req, res) => {
  const lead = {
    name: req.body.Name,
    phone: req.body.Phone,
    tour: req.body.tour,
    date: req.body.date,
    guests: req.body.guests,
    leadId: req.body.tranid,
  };

  // Сохранить в БД, отправить в Telegram, и т.д.
  console.log('Новый лид:', lead);
  res.send('ok');
});

app.listen(3000);
```

### Поля формы для туризма

Рекомендуемый набор полей:
- Имя (текст, обязательное)
- Телефон (tel, обязательное)
- Email (email, опционально)
- Экскурсия (select: Desert Safari / Burj Khalifa / City Tour / Dhow Cruise)
- Дата (date)
- Количество гостей (select: 1-10)
- Комментарий (textarea)
- Откуда узнали (select: Instagram / WhatsApp / Друзья / Google)

---

## 6. Tilda API

### Обзор

Tilda API позволяет программно получать данные проектов и страниц. Доступен только на тарифе **Business**.

**Base URL:** `https://api.tildacdn.info`

**Аутентификация:** каждый запрос требует `publickey` и `secretkey`.
Получить ключи: Site Settings -> Export -> API Integration.

**Rate Limit:** 150 запросов/час.

### Endpoints

| Endpoint | Параметры | Ответ |
|----------|-----------|-------|
| `/v1/getprojectslist` | publickey, secretkey | Список всех проектов |
| `/v1/getprojectinfo` | + projectid | Детали проекта, настройки |
| `/v1/getpageslist` | + projectid | Список страниц проекта |
| `/v1/getpage` | + pageid | Информация + body HTML |
| `/v1/getpagefull` | + pageid | Информация + полный HTML |
| `/v1/getpageexport` | + pageid | Экспорт body HTML + маппинг файлов |
| `/v1/getpagefullexport` | + pageid | Полный экспорт + маппинг файлов |

### Примеры

**Получить список страниц:**
```bash
curl "https://api.tildacdn.info/v1/getpageslist/?\
publickey=YOUR_PUBLIC_KEY&\
secretkey=YOUR_SECRET_KEY&\
projectid=12345"
```

**Ответ:**
```json
{
  "status": "FOUND",
  "result": [
    {
      "id": "67890",
      "projectid": "12345",
      "title": "Desert Safari Landing",
      "descr": "Лендинг экскурсии в пустыню",
      "alias": "desert-safari",
      "date": "2026-02-13 10:30:00",
      "published": "1644756600"
    }
  ]
}
```

**Получить HTML страницы:**
```bash
curl "https://api.tildacdn.info/v1/getpage/?\
publickey=YOUR_PUBLIC_KEY&\
secretkey=YOUR_SECRET_KEY&\
pageid=67890"
```

### Webhook при публикации

Tilda может отправлять GET-запрос при публикации страницы:

```
https://yoursite.com/tilda-publish?pageid=67890&projectid=12345&published=1&publickey=KEY
```

**Применение:** автоматическая синхронизация контента с вашим сервером, обновление кеша, уведомление команды.

---

## 7. Интеграция с CRM

### Notion как CRM для лидов

**Схема:** Tilda Form -> Webhook -> Make.com/n8n -> Notion Database

**Notion Database "Лиды":**
| Имя | Телефон | Экскурсия | Дата | Статус | Источник |
|-----|---------|-----------|------|--------|----------|
| Иван | +7... | Desert Safari | 15.03 | Новый | Instagram |

**Настройка через Make.com:**
1. Trigger: Webhook -> Custom webhook -> скопировать URL
2. Вставить URL в Tilda: Site Settings -> Forms -> Webhook
3. Action: Notion -> Create a Database Item
4. Маппинг полей: Name -> Имя, Phone -> Телефон, tour -> Экскурсия
5. Статус по умолчанию: "Новый"

### AmoCRM (встроенная интеграция)

1. Site Settings -> Forms -> AmoCRM -> авторизоваться
2. Настроить маппинг полей
3. Лиды автоматически создаются в воронке AmoCRM
4. Можно настроить автоматические задачи менеджерам

### Bitrix24

1. Site Settings -> Forms -> Bitrix24
2. Ввести URL портала (`yourcompany.bitrix24.ru`)
3. Авторизоваться
4. Лиды попадают в CRM Bitrix24

### Zapier/Make.com -- универсальный коннектор

Через автоматизаторы можно связать Tilda с любым сервисом:
- **Tilda -> Make.com -> Notion** (CRM)
- **Tilda -> Zapier -> Google Sheets** (таблица лидов)
- **Tilda -> n8n -> Telegram + Google Sheets** (одновременно)
- **Tilda -> Make.com -> WhatsApp Business API** (автоответ клиенту)

---

## 8. Платёжные системы

### Поддерживаемые системы

Tilda интегрируется с 35+ платёжными системами. Подключение: Site Settings -> Payment Systems.

**Международные:**
| Система | Комиссия | Валюты | ОАЭ |
|---------|----------|--------|-----|
| **Stripe** | 2.9% + $0.30 | 135+ | Работает |
| **PayPal** | 3.4% + фикс | 25+ | Работает |
| **2Checkout (Verifone)** | 3.5% + $0.35 | 45+ | Работает |

**СНГ-ориентированные:**
| Система | Комиссия | Валюты |
|---------|----------|--------|
| **CloudPayments** | от 2.3% | RUB, KZT, USD, EUR |
| **ЮKassa** | от 3.5% | RUB |
| **Robokassa** | от 3.9% | RUB |
| **Fondy** | от 2.5% | UAH, RUB, EUR |
| **LiqPay** | от 2.75% | UAH, USD, EUR |

### Настройка Stripe для ОАЭ

1. Зарегистрироваться на stripe.com (ОАЭ поддерживается)
2. Получить Publishable Key и Secret Key
3. Tilda: Site Settings -> Payment Systems -> Stripe
4. Вставить ключи
5. Установить валюту: AED
6. Опубликовать страницу

**Результат:** клиент выбирает товар-экскурсию -> корзина -> Stripe Checkout -> оплата -> подтверждение.

### Криптоплатежи

Для USDT/Bitcoin используйте T123 блок + внешний сервис (CryptoCloud, NOWPayments):
1. Зарегистрироваться на cryptocloud.plus
2. Получить API ключ
3. Сгенерировать платёжную ссылку для каждого товара
4. Вставить ссылку в CTA-кнопку на Tilda

### Мультивалютность

Tilda поддерживает установку валюты в настройках магазина. Для мультивалютного сайта:
- Создайте отдельные страницы для каждой валюты (AED, USD, RUB)
- Или используйте Stripe (автоматическая конвертация)
- Указывайте цены в AED как основную, с пометкой "~$XX USD"

---

## 9. Кастомизация (HTML/CSS/JS)

### T123 блок -- встроенный HTML

Блок "Embed HTML code" (категория "Other") позволяет вставлять произвольный HTML, CSS и JavaScript.

**Где добавлять код:**
1. **T123 блок** -- на конкретную страницу (локально)
2. **Site Settings -> More -> HTML Code for HEAD** -- в `<head>` всех страниц (глобально)
3. **Page Settings -> Advanced -> HTML Code for HEAD** -- в `<head>` конкретной страницы

### JavaScript API Tilda

**t_onReady -- ожидание загрузки DOM:**
```javascript
t_onReady(function() {
  // Код выполнится после загрузки Tilda
  console.log('Tilda loaded');
});
```

**jQuery доступен глобально** (версия 1.10.2):
```javascript
$(document).ready(function() {
  // jQuery код
  $('.t-btn').on('click', function() {
    console.log('Button clicked');
  });
});
```

**События форм (tildaForm):**
```javascript
// Перехват успешной отправки формы
document.querySelector('.js-form-proccess').addEventListener(
  'tildaform:aftersuccess', function(e) {
    var form = e.target;
    var leadId = form.tildaTranId;
    var orderId = form.tildaOrderId;

    // Отправить событие в GA4
    gtag('event', 'generate_lead', {
      currency: 'AED',
      value: 180,
      lead_id: leadId
    });

    // Redirect на thank you page
    window.location.href = '/thank-you';
  }
);
```

### Калькулятор стоимости тура (пример)

```html
<!-- T123 блок: Калькулятор Desert Safari -->
<div id="tour-calculator" style="max-width: 500px; margin: 0 auto; padding: 30px;
     background: #f8f9fa; border-radius: 12px;">
  <h3 style="text-align: center;">Рассчитать стоимость</h3>

  <label>Количество гостей:</label>
  <select id="guests" onchange="calculate()">
    <option value="1">1</option>
    <option value="2" selected>2</option>
    <option value="3">3</option>
    <option value="4">4</option>
    <option value="5">5+</option>
  </select>

  <label>Тип тура:</label>
  <select id="tourType" onchange="calculate()">
    <option value="180">Standard (180 AED/чел)</option>
    <option value="350">VIP (350 AED/чел)</option>
    <option value="1200">Private (1200 AED/группа)</option>
  </select>

  <label><input type="checkbox" id="transfer" onchange="calculate()">
    Трансфер из отеля (+50 AED)</label>

  <div id="result" style="font-size: 24px; font-weight: bold;
       text-align: center; margin-top: 20px; color: #e67e22;">
    Итого: 360 AED
  </div>
</div>

<script>
function calculate() {
  var guests = parseInt(document.getElementById('guests').value);
  var price = parseInt(document.getElementById('tourType').value);
  var transfer = document.getElementById('transfer').checked ? 50 : 0;

  var total;
  if (price === 1200) {
    total = price + transfer; // Private -- фикс за группу
  } else {
    total = (price * guests) + transfer;
  }

  document.getElementById('result').textContent = 'Итого: ' + total + ' AED';
}
</script>
```

### CSS-кастомизация

```css
/* T123 блок: глобальные стили */
<style>
/* Скруглить все кнопки */
.t-btn { border-radius: 30px !important; }

/* Кастомный цвет CTA */
.t-btn_md {
  background-color: #e67e22 !important;
  border-color: #e67e22 !important;
}
.t-btn_md:hover {
  background-color: #d35400 !important;
}

/* Скрыть блок на мобильном */
@media (max-width: 640px) {
  #rec123456789 { display: none; }
}

/* Кастомный шрифт для заголовков */
.t-title { font-family: 'Montserrat', sans-serif !important; }
</style>
```

---

## 10. Мультиязычность (RU/EN/AR)

### Подходы

**Подход 1: Отдельные проекты (рекомендуется)**

Требуется Business план (5 сайтов). Каждый язык = отдельный проект:
- `dubai-tours.com` -- английский (основной)
- `dubai-tours.com/ru/` -- русский (подпапка через редирект)
- Или: `en.dubai-tours.com`, `ru.dubai-tours.com` (субдомены)

**Подход 2: Отдельные страницы в одном проекте**

Personal план. Создать папки:
- `/` -- главная (EN)
- `/ru/` -- русская версия
- `/ar/` -- арабская версия

Добавить языковой переключатель через меню ME204 или кастомный блок.

### Языковой переключатель (JS)

```html
<!-- T123 блок: переключатель языка -->
<div id="lang-switcher" style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
  <a href="/" style="margin: 0 5px;">EN</a>
  <a href="/ru/" style="margin: 0 5px;">RU</a>
  <a href="/ar/" style="margin: 0 5px;">AR</a>
</div>
```

### RTL для арабского

```css
/* T123 блок: RTL стили для арабской версии */
<style>
/* Применять только на /ar/ страницах */
body { direction: rtl; }
.t-text, .t-title, .t-descr { text-align: right; }
.t-container { direction: rtl; }

/* Исключения для номеров и кода */
.t-btn, .t-input { direction: ltr; }
</style>
```

### SEO для мультиязычности

В Page Settings -> Advanced -> HTML Code for HEAD добавить hreflang:

```html
<link rel="alternate" hreflang="en" href="https://dubai-tours.com/" />
<link rel="alternate" hreflang="ru" href="https://dubai-tours.com/ru/" />
<link rel="alternate" hreflang="ar" href="https://dubai-tours.com/ar/" />
<link rel="alternate" hreflang="x-default" href="https://dubai-tours.com/" />
```

### Weglot (автоперевод)

Tilda интегрирована с Weglot -- сервисом автоматического перевода:
1. Зарегистрироваться на weglot.com
2. Получить API Key
3. Site Settings -> More -> HTML Code for HEAD -> вставить скрипт Weglot
4. Weglot автоматически переведёт контент, добавит переключатель

**Цена Weglot:** от $15/мес (10,000 слов). Для небольших сайтов -- экономичнее ручного перевода.

---

## 11. SEO

### Базовая настройка

**Site Settings -> SEO:**
- Title: "Dubai Tours & Excursions | Desert Safari, Burj Khalifa, Dhow Cruise"
- Description: "Best prices for Dubai excursions. Desert Safari from 180 AED. Book online."
- Favicon: загрузить .ico/.png

**Page Settings (для каждой страницы):**
- Title (уникальный для каждой страницы)
- Description (уникальное, 150-160 символов)
- URL alias: `/desert-safari` (не `/page12345`)
- Open Graph image (1200x630)

### Встроенные SEO-инструменты

- **SEO-ассистент:** автоматически проверяет H1, meta, alt-теги, скорость
- **Sitemap.xml:** генерируется автоматически
- **Robots.txt:** генерируется автоматически
- **HTTPS/SSL:** включается одной кнопкой (Site Settings -> SEO -> HTTPS)
- **Alt-теги:** задаются для каждого изображения в Content Panel

### Open Graph

Page Settings -> OG:
- og:title -- заголовок для соцсетей
- og:description -- описание для соцсетей
- og:image -- превью 1200x630 (шаблон: фото тура + лого + цена)

### Schema.org для экскурсий

Добавить в Page Settings -> Advanced -> HTML Code for HEAD:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TouristTrip",
  "name": "Desert Safari Dubai",
  "description": "Unforgettable desert safari experience with BBQ dinner, camel ride, and entertainment show",
  "touristType": "Adventure",
  "offers": {
    "@type": "Offer",
    "price": "180",
    "priceCurrency": "AED",
    "availability": "https://schema.org/InStock"
  },
  "provider": {
    "@type": "TravelAgency",
    "name": "Dubai Tours",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Dubai",
      "addressRegion": "Tecom",
      "addressCountry": "AE"
    },
    "telephone": "+971-XX-XXX-XXXX"
  },
  "itinerary": {
    "@type": "ItemList",
    "itemListElement": [
      {"@type": "ListItem", "position": 1, "name": "Hotel pickup"},
      {"@type": "ListItem", "position": 2, "name": "Dune bashing"},
      {"@type": "ListItem", "position": 3, "name": "Camel ride"},
      {"@type": "ListItem", "position": 4, "name": "BBQ dinner"},
      {"@type": "ListItem", "position": 5, "name": "Entertainment show"}
    ]
  }
}
</script>
```

### Скорость загрузки

Tilda использует CDN (~5,500 серверов, 100+ точек присутствия). Дополнительная оптимизация:
- Сжимайте изображения перед загрузкой (TinyPNG, WebP)
- Используйте Lazy Loading (встроено в Tilda)
- Минимизируйте кастомные скрипты
- Не загружайте тяжёлые видео напрямую -- используйте YouTube/Vimeo embed

---

## 12. Аналитика

### Подключение счётчиков

**Site Settings -> Analytics:**

| Сервис | Поле | Пример |
|--------|------|--------|
| **Google Analytics 4** | Measurement ID | G-XXXXXXXXXX |
| **Яндекс.Метрика** | Counter ID | 12345678 |
| **Facebook Pixel** | Pixel ID | 987654321 |
| **Google Tag Manager** | Container ID | GTM-XXXXXXX |

### Отслеживание событий

**Через GA4 (в T123 блоке):**
```javascript
// Отслеживание клика по CTA
t_onReady(function() {
  document.querySelectorAll('.t-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      gtag('event', 'cta_click', {
        event_category: 'engagement',
        event_label: btn.textContent.trim()
      });
    });
  });
});
```

**Через Яндекс.Метрику:**
```javascript
// Цель: отправка формы
t_onReady(function() {
  document.querySelector('.js-form-proccess').addEventListener(
    'tildaform:aftersuccess', function() {
      ym(12345678, 'reachGoal', 'form_submit');
    }
  );
});
```

### UTM-метки

Tilda автоматически сохраняет UTM-параметры из URL и передаёт их в формы (если включена опция "Send cookies" в webhook).

**Формат ссылок для рекламы:**
```
https://dubai-tours.com/desert-safari?utm_source=instagram&utm_medium=story&utm_campaign=march2026
```

### Воронка конверсии

```
Посетитель -> Просмотр страницы (GA4 pageview)
           -> Скролл 50% (GA4 scroll)
           -> Клик CTA (custom event)
           -> Открытие формы (custom event)
           -> Отправка формы (tildaform:aftersuccess)
           -> Thank You page (conversion)
```

---

## 13. Практические примеры ОАЭ

### Пример 1: Лендинг "Desert Safari"

**Структура (8 блоков, 1 страница):**
- CR400: "Сафари в пустыне Дубая -- от 180 AED" + полноэкранное фото заката
- AB300: Описание (джипы, верблюды, BBQ, шоу-программа)
- GL14: Слайдер 8 фото (закат, дюны, лагерь, еда)
- FT300: Что входит (6 иконок: транспорт, ужин, шоу, фото, напитки, верблюды)
- PR100: 3 тарифа (Standard 180 / VIP 350 / Private 1200 AED)
- CL100: Отзывы (4 карточки с фото клиентов)
- BF400: Форма (имя, телефон, дата, гости, тип тура)
- FT500: Footer (WhatsApp, Instagram, Telegram, адрес офиса)

**Интеграции:** Telegram бот + Google Sheets + Яндекс.Метрика + GA4

### Пример 2: Каталог экскурсий (мультистраница)

**Страницы:**
- `/` -- главная (Cover + категории экскурсий)
- `/desert-safari` -- Desert Safari лендинг
- `/city-tour` -- City Tour лендинг
- `/burj-khalifa` -- Burj Khalifa билеты
- `/dhow-cruise` -- Dhow Cruise вечерний
- `/abu-dhabi` -- Abu Dhabi Full Day
- `/yacht-charter` -- Аренда яхт (каталог из ST315N)
- `/contacts` -- Контакты, карта офиса

**Навигация:** ME204 (горизонтальное меню) с логотипом и CTA-кнопкой "Забронировать"

### Пример 3: Мультисайт (Business план)

3 проекта на одном аккаунте:
1. **dubai-tours.com** -- экскурсии (Сухейль)
2. **dubai-cars.com** -- аренда авто (Марсель)
3. **dubai-yachts.com** -- яхты (Муфамад)

Общие элементы: дизайн, цветовая схема, footer с перекрёстными ссылками.

### WhatsApp CTA-кнопка

```
https://wa.me/971XXXXXXXXX?text=Здравствуйте!%20Хочу%20забронировать%20Desert%20Safari%20на%20[ДАТА]%20для%20[КОЛИЧЕСТВО]%20гостей
```

Вставить как ссылку в CTA-кнопку Tilda.

---

## 14. Хостинг, домен, production

### Хостинг

Tilda предоставляет хостинг на всех тарифах:
- CDN: 100+ точек присутствия, ~5,500 серверов
- Uptime: 99.9%+
- SSL/HTTPS: бесплатный Let's Encrypt
- Хранилище: 50 МБ (Free), 1 ГБ (Personal/Business)

### Подключение домена

1. Купить домен (Namecheap, GoDaddy, REG.RU)
2. В DNS-настройках домена добавить A-запись:
   - Host: `@`
   - Value: IP-адрес Tilda (указан в Site Settings -> Domain)
3. Или CNAME для субдомена:
   - Host: `www`
   - Value: `cname.tilda.ws`
4. В Tilda: Site Settings -> Domain -> ввести домен
5. Подождать 24 часа на обновление DNS
6. Включить HTTPS: Site Settings -> SEO -> HTTPS

### Экспорт кода (Business)

Site Settings -> Export -> Download as .zip:
- HTML файлы страниц
- CSS стили
- JavaScript
- Изображения
- Шрифты

**Ограничения экспорта:**
- SSL-сертификат отключается -- нужен сторонний SSL на хостинге
- Шрифты ParaType/type.today требуют активной подписки Tilda
- Приём форм требует активной подписки (формы перестанут работать без неё)
- **НЕ экспортируются:** Tilda CRM, Tilda Members, Product Catalog (работают только на Tilda)
- Защита паролем страниц отключается после экспорта

**Применение:** перенос на свой хостинг, бэкап, интеграция с кастомным backend.

### Production чеклист

- [ ] Домен подключён и работает
- [ ] HTTPS включён
- [ ] Все страницы опубликованы
- [ ] Формы протестированы (лиды приходят в Telegram/Email)
- [ ] SEO: title, description, OG для каждой страницы
- [ ] Schema.org добавлена (TouristTrip)
- [ ] Аналитика подключена (GA4 + Метрика)
- [ ] Мобильная версия проверена
- [ ] Скорость проверена (PageSpeed Insights > 80)
- [ ] Платёжная система протестирована (тестовый платёж)
- [ ] Языковые версии работают (RU/EN)
- [ ] WhatsApp CTA ведёт на правильный номер
- [ ] Favicon загружен
- [ ] 404-страница настроена

---

## Безопасность

### Данные форм

- Tilda хранит лиды в встроенной CRM (Site Settings -> Leads)
- Данные передаются по HTTPS
- Webhook: используйте HTTPS endpoint, валидируйте данные на сервере
- Не храните чувствительные данные (пароли, карты) в формах Tilda

### API ключи

- Не публикуйте secretkey в клиентском коде
- Ротируйте ключи при подозрении на утечку
- Ограничьте доступ к API Integration в настройках

### Резервные копии

- Экспортируйте код регулярно (Business план)
- Дублируйте проект в Tilda (Dashboard -> Duplicate)
- Сохраняйте тексты/изображения отдельно

---

## Стоимость

| Компонент | Цена |
|----------|------|
| Tilda Personal | $15/мес |
| Домен (.com) | $10-15/год |
| Weglot (мультиязычность) | от $15/мес |
| Make.com (автоматизация) | от $9/мес |
| **Итого (минимум)** | **$15-25/мес** |
| **Итого (полный)** | **$40-55/мес** |

---

## Полезные ссылки

- **Справочный центр:** help.tilda.cc
- **Обучение:** tilda.education
- **Блог:** blog-en.tilda.cc
- **Zero Block:** zero.tilda.cc
- **API:** help.tilda.cc/api
- **Тарифы:** tilda.cc/pricing
- **Шаблоны:** tilda.cc/tpls

---

## Структура справочника

### References
- `faq.md` -- 12 частых вопросов (тарифы, формы, интеграции)
- `troubleshooting.md` -- 12 типичных проблем и решений
- `cheatsheet.md` -- шпаргалка: блоки, API, CSS, JS, SEO

---

**Версия:** 1.0
**Дата:** 13.02.2026
**Автор:** Claude Code Agent
**Для:** Туристический бизнес в ОАЭ (Сухейль)

---

## Experience

Этот скилл накапливает опыт в папке `experience/`:
- `_index.md` -- критические уроки (читать при активации!)
- `fixes/` -- исправленные ошибки
- `improvements/` -- найденные улучшения
- `patterns/` -- повторяющиеся паттерны
- `warnings/` -- что НЕ делать

При завершении работы: если был урок -- предложить записать в опыт.

---

## Ресурсы скилла

| Файл | Описание |
|------|----------|
| references/faq.md | Часто задаваемые вопросы |
| references/troubleshooting.md | Решение проблем |
| references/cheatsheet.md | Шпаргалка |
