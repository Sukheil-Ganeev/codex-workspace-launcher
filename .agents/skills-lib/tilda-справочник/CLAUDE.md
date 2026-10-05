# CLAUDE.md -- tilda-справочник

## Общее описание

**Название:** tilda-справочник
**Тип:** Production-ready руководство по Tilda Publishing
**Назначение:** Создание лендингов, каталогов и интернет-магазинов для туристического бизнеса в ОАЭ (Дубай). Покрывает Zero Code блоки, кастомный HTML/CSS/JS, Tilda API, интеграции с CRM (Notion, AmoCRM), мессенджерами (Telegram, WhatsApp), платёжными системами (Stripe, PayPal, крипто), SEO, мультиязычные сайты (RU/EN/AR).
**Целевая аудитория:** Сухейль -- предприниматель в сфере туризма ОАЭ, семейный бизнес (экскурсии, яхты, аренда авто).
**Версия:** 1.0
**Дата создания:** 13.02.2026
**Автор:** Claude Code Agent

---

## Структура файлов

```
tilda-справочник/
├── SKILL.md                    # Основной справочник (~5000 слов, 39 KB)
├── README.md                   # Описание структуры и навигация (3 KB)
├── CLAUDE.md                   # Этот файл -- метаданные и карта скилла
├── CHANGELOG.md                # История изменений
└── references/
    ├── faq.md                  # 12 частых вопросов (9 KB)
    ├── troubleshooting.md      # 12 типичных проблем и решений (10 KB)
    └── cheatsheet.md           # Шпаргалка: блоки, API, CSS, JS, SEO (7 KB)
```

### Описание каждого файла

| Файл | Описание |
|------|----------|
| **SKILL.md** | Полный справочник: 14 разделов, от обзора платформы до production-чеклиста. Содержит примеры кода (HTML, CSS, JS, JSON, Bash), таблицы сравнения, пошаговые инструкции. |
| **README.md** | Краткое описание скилла, таблица всех 14 разделов, требования к тарифам, быстрый старт (5 шагов). |
| **references/faq.md** | 12 вопросов с развёрнутыми ответами. Покрывает тарифы, магазин, Telegram, мультиязычность, платежи, формы, WhatsApp, скорость, Schema.org, Notion CRM, калькулятор, Tilda vs Shopify. |
| **references/troubleshooting.md** | 12 проблем с симптомами и решениями. Покрывает формы, CSS, JS, скорость, мобильную версию, Telegram webhook, оплату, SEO-индексацию, домен, API rate limit, RTL, pop-up. |
| **references/cheatsheet.md** | Компактная шпаргалка: топ-18 блоков для туризма, 7 API endpoints, webhook-формат, CSS-хаки, JS-паттерны, SEO-чеклист, таблица тарифов, 12 приёмников форм, WhatsApp CTA-ссылка, полезные ссылки. |

---

## 14 разделов SKILL.md

| # | Раздел | Содержание |
|---|--------|------------|
| 1 | **Обзор платформы и выбор тарифа** | Что такое Tilda, 3 тарифа (Free $0 / Personal $15 / Business $25), сравнение Tilda vs Shopify vs WordPress, рекомендация для туризма |
| 2 | **Быстрый старт: лендинг за 2 часа** | 7-шаговый план (регистрация -> публикация), структура лендинга "Desert Safari" из 10 блоков |
| 3 | **Zero Code блоки -- каталог для туризма** | 16 категорий блоков с префиксами (CR, AB, FT, GL, ST, BF, PR, TM, TL, TX, CL, FT, ME, MP, ST, FD), Zero Block визуальный редактор, breakpoints |
| 4 | **Каталог и карточки продуктов (Tilda Store)** | Настройка магазина, карточка товара-экскурсии с опциями, до 5000 товаров, 30 вариантов, фильтры, промокоды, CSV импорт/экспорт |
| 5 | **Формы и сбор лидов** | 12+ приёмников (Email, Google Sheets, Telegram, Webhook, AmoCRM, Bitrix24, MailChimp, Slack, Salesforce, HubSpot, UniSender, GetResponse), настройка @TildaFormsBot, webhook JSON-формат, Node.js-приёмник, рекомендуемые поля |
| 6 | **Tilda API** | Base URL api.tildacdn.info, 7 endpoints, publickey+secretkey аутентификация, 150 req/hr rate limit, примеры curl, webhook при публикации. Только Business план |
| 7 | **Интеграция с CRM** | Notion через Make.com/n8n, AmoCRM (встроенная), Bitrix24, универсальные коннекторы Zapier/Make.com/n8n |
| 8 | **Платёжные системы** | 35+ систем: Stripe (рекомендуется для ОАЭ, 2.9%), PayPal, 2Checkout, CloudPayments, ЮKassa, Robokassa, Fondy, LiqPay. Настройка Stripe для AED. Криптоплатежи через CryptoCloud/NOWPayments. Мультивалютность |
| 9 | **Кастомизация (HTML/CSS/JS)** | T123 блок, 3 места для кода (T123, HEAD сайта, HEAD страницы), t_onReady(), jQuery 1.10.2, события tildaForm, полный пример калькулятора стоимости тура, CSS-кастомизация (скругление кнопок, мобильное скрытие, шрифты) |
| 10 | **Мультиязычность (RU/EN/AR)** | 2 подхода (отдельные проекты / папки), языковой переключатель JS, RTL для арабского, hreflang SEO-теги, Weglot автоперевод ($15+/мес) |
| 11 | **SEO** | Title/Description/URL alias, SEO-ассистент, sitemap/robots автогенерация, HTTPS, alt-теги, Open Graph 1200x630, Schema.org TouristTrip JSON-LD с примером, CDN 5500 серверов, оптимизация скорости |
| 12 | **Аналитика** | GA4, Яндекс.Метрика, Facebook Pixel, GTM, отслеживание событий JS, UTM-метки, воронка конверсии (6 шагов) |
| 13 | **Практические примеры ОАЭ** | Лендинг "Desert Safari" (8 блоков), каталог экскурсий (8 страниц), мультисайт Business (3 проекта: tours/cars/yachts), WhatsApp CTA-кнопка |
| 14 | **Хостинг, домен, production** | CDN 99.9% uptime, SSL Let's Encrypt, подключение домена (A-запись, CNAME), экспорт кода (Business), ограничения экспорта (5 пунктов), production чеклист (14 пунктов) |

Дополнительные секции в SKILL.md:
- **Безопасность** -- защита форм, API ключей, резервные копии
- **Стоимость** -- итого $15-55/мес (Tilda + домен + Weglot + Make.com)
- **Полезные ссылки** -- 7 ресурсов (help.tilda.cc, tilda.education, zero.tilda.cc и др.)
- **Experience** -- протокол накопления опыта в папке experience/
- **Ресурсы скилла** -- таблица файлов references/

---

## 12 вопросов FAQ (references/faq.md)

1. **Какой тариф Tilda нужен для туристического бизнеса?** -- Personal $15 для 90% задач, Business $25 для нескольких сайтов/API
2. **Можно ли сделать полноценный магазин экскурсий с оплатой?** -- Да, Tilda Store до 5000 товаров, Stripe/PayPal, корзина, промокоды
3. **Как настроить отправку заявок в Telegram бот?** -- @TildaFormsBot -> Start -> API Key -> Site Settings -> Forms -> Telegram
4. **Как сделать мультиязычный сайт (RU/EN/AR)?** -- Отдельные проекты (Business) или папки (Personal), Weglot для автоперевода
5. **Какие платёжные системы работают в ОАЭ?** -- Stripe (основная), PayPal, 2Checkout. НЕ работают: CloudPayments, ЮKassa, Robokassa
6. **Как добавить выбор даты тура в форму?** -- Поле типа Date в BF400/BF200, или flatpickr через T123
7. **Можно ли подключить WhatsApp с автотекстом?** -- Да, через wa.me/971XXX?text=... в CTA-кнопке
8. **Как оптимизировать скорость загрузки?** -- Сжать изображения (WebP), YouTube embed вместо видео, max 15-20 блоков, 1-2 шрифта
9. **Как настроить Schema.org для экскурсий?** -- JSON-LD TouristTrip в Page Settings -> HEAD, проверка через Rich Results Test
10. **Можно ли интегрировать с Notion как CRM?** -- Да, через Make.com/Zapier (Tilda -> Webhook -> Make.com -> Notion Database)
11. **Как сделать калькулятор стоимости тура?** -- T123 блок с HTML/JS, пример в SKILL.md раздел 9
12. **Tilda vs Shopify -- когда что использовать?** -- Tilda для лендингов/каталогов до 50 товаров, Shopify для полноценного e-commerce

---

## 12 проблем Troubleshooting (references/troubleshooting.md)

1. **Форма не отправляет данные** -- проверить приёмник Active, выбран в Content Panel, страница опубликована, Email подтверждён
2. **CSS стили не применяются** -- добавить !important, проверить специфичность, использовать ID блока #recXXX, очистить кеш
3. **JavaScript не работает** -- обернуть в t_onReady(), проверить консоль F12, jQuery доступен как $, не работает в Preview
4. **Страница грузится медленно** -- сжать изображения WebP до 300 КБ, YouTube embed, max 15-20 блоков, max 2 шрифта
5. **Мобильная версия выглядит криво** -- настроить breakpoints в Zero Block, media queries в CSS, Visibility -> скрыть на Mobile
6. **Telegram webhook не приходит** -- перезапросить ключи у @TildaFormsBot, бот добавлен в группу, /start в группе, Telegram Active
7. **Оплата не проходит (Stripe/PayPal)** -- live-ключи (не test), валюта AED совпадает, KYC пройден, проверить Stripe Logs
8. **SEO: страница не индексируется Google** -- robots.txt не блокирует, добавить в Search Console, Title/Description заполнены, HTTPS включён
9. **Домен не подключается** -- DNS обновляется до 24ч, проверить A-запись и CNAME, whatsmydns.net, Cloudflare прокси отключить
10. **API возвращает ошибку 429** -- лимит 150 req/hr, кешировать ответы Redis, использовать webhook вместо polling, getpagefull
11. **RTL (арабский) текст отображается неправильно** -- CSS direction: rtl, text-align: right, исключить input/btn, Google Fonts Arabic
12. **Pop-up не появляется** -- блок на той же странице, ссылка #popup:recXXX, AdBlock отключить, переопубликовать

---

## Структура cheatsheet (references/cheatsheet.md)

| Секция | Содержание |
|--------|------------|
| **Топ блоки для туризма** | Таблица 18 блоков (CR400, CR300, AB300, GL14, GL100, FT300, ST200, ST315N, ST100, BF400, BF200, PR100, CL100, ME204, ME401, MP100, FT500, T123) |
| **Tilda API Endpoints** | Base URL, 7 endpoints с параметрами, пример запроса и ответа |
| **Webhook формат** | POST application/x-www-form-urlencoded, поля (Name, Phone, Email, tour, date, guests, tranid, formid) |
| **CSS хаки** | 7 рецептов: скруглить кнопки, цвет CTA, скрыть на мобильном, шрифт, стилизация блока, sticky header, RTL |
| **JS паттерны** | 4 паттерна: t_onReady, tildaform:aftersuccess, Яндекс.Метрика reachGoal, jQuery |
| **SEO чеклист** | Таблица 12 элементов (Title, Description, H1, Alt, URL alias, OG image, HTTPS, Sitemap, Robots, Schema.org, hreflang, Favicon) |
| **Тарифы (2026)** | Таблица сравнения Free/Personal/Business по 10 параметрам |
| **Приёмники форм** | Таблица 12 сервисов с путями настройки |
| **WhatsApp CTA ссылка** | Шаблон wa.me с URL-encode |
| **Полезные ссылки** | 8 ресурсов (help.tilda.cc, tilda.education, zero.tilda.cc, tilda.cc/tpls, help.tilda.cc/api, tilda.cc/pricing, blog-en.tilda.cc, webhook.site) |

---

## Связанная презентация

| Параметр | Значение |
|----------|----------|
| **Путь HTML** | `D:/Downloads/Skill_Presentations/tilda/presentation.html` |
| **Путь PDF** | `D:/Downloads/Skill_Presentations/tilda/output/tilda.pdf` |
| **Тема дизайна** | "Canvas Flow" -- светлая тема с warm coral палитрой |
| **Размер HTML** | 84 KB |
| **Размер PDF** | 4.5 MB |
| **Количество слайдов** | 18 |
| **Шрифты** | Plus Jakarta Sans (заголовки), DM Sans (текст), Fira Code (код) |
| **Цветовая палитра** | warm coral #FF7B54, purple #6E56CF, teal #2A9D8F, coral #E76F51 |
| **Фон** | #FAF7F2 (warm off-white) с canvas-текстурой |

### Структура слайдов презентации (18 слайдов)

| # | Секция | Заголовок |
|---|--------|-----------|
| 01 | Справочник 2026 | Tilda 2026 (титульный, hero) |
| 02 | Навигация | Содержание |
| 03 | Философия | Блоковая система Tilda |
| 04 | Тарифы | Планы и цены (2026) |
| 05 | Блоки | Библиотека блоков |
| 06 | Дизайн | Zero Block -- визуальный редактор |
| 07 | Дизайн | Типографика и стили |
| 08 | Эффекты | Анимации и эффекты |
| 09 | Лиды | Формы и сбор лидов |
| 10 | API | Tilda API |
| 11 | SEO | SEO в Tilda |
| 12 | E-commerce | Tilda Store (магазин) |
| 13 | Архитектура | Структура лендинга |
| 14 | Локализация | Мультиязычность (RU/EN/AR) |
| 15 | Экосистема | Интеграции |
| 16 | Кастомизация | HTML / CSS / JS в Tilda |
| 17 | Сравнение | Tilda vs Конкуренты |
| 18 | Production | Чек-лист публикации |

---

## Ключевые факты

### Tilda
- **Тарифы:** Free ($0, 50 стр), Personal ($15/мес, 500 стр, 1 сайт), Business ($25/мес, 5 сайтов, API, экспорт)
- **Блоков:** 550+ готовых + Zero Block (кастомный дизайн)
- **Товаров:** до 5000, до 30 вариантов
- **CDN:** 5500 серверов, 100+ точек, 99.9% uptime
- **Хранилище:** 50 MB (Free), 1 GB (Personal/Business)

### Telegram интеграция
- **Бот:** @TildaFormsBot (НЕ @BotFather!) -- специальный бот Tilda для приёма лидов
- **Процесс:** написать @TildaFormsBot -> Start -> получить API Key + Secret Key -> вставить в Site Settings -> Forms -> Telegram
- **Для групп:** добавить @TildaFormsBot в группу -> /start -> API Key может быть отрицательным

### API
- **Base URL:** https://api.tildacdn.info
- **Rate Limit:** 150 запросов/час (жёсткий лимит)
- **Аутентификация:** publickey + secretkey (Site Settings -> Export -> API Integration)
- **Endpoints:** 7 штук (getprojectslist, getprojectinfo, getpageslist, getpage, getpagefull, getpageexport, getpagefullexport)
- **Только тариф:** Business ($25/мес)

### Платежи в ОАЭ
- **Работают:** Stripe (2.9% + $0.30), PayPal (3.4%), 2Checkout (3.5%)
- **НЕ работают в ОАЭ:** CloudPayments, ЮKassa, Robokassa (только РФ/СНГ)
- **Криптоплатежи:** через CryptoCloud/NOWPayments + T123 блок

### Ограничения экспорта кода
- SSL-сертификат отключается -- нужен сторонний SSL
- Шрифты ParaType/type.today требуют активной подписки Tilda
- Формы требуют активной подписки (перестанут работать)
- НЕ экспортируются: Tilda CRM, Tilda Members, Product Catalog
- Защита паролем страниц отключается

### Стоимость развёртывания
- Минимум: $15-25/мес (Tilda + домен)
- Полный: $40-55/мес (+ Weglot + Make.com)

---

## Связанные скиллы

| Скилл | Связь |
|-------|-------|
| **payment-integration** | Платёжные системы: Stripe, PayPal, крипто -- детальная интеграция |
| **seo** | Расширенная SEO-оптимизация: Schema.org, Core Web Vitals, GA4, Search Console |
| **html-css** | Кастомизация Tilda: T123 блоки, CSS !important, jQuery, адаптив |
| **shopify-справочник** | Альтернатива для полноценного e-commerce (>50 товаров, инвентарь, подписки) |

---

## Исследование альтернатив

В рамках создания скилла было проведено исследование 15 конструкторов сайтов как альтернатив Tilda.

**Формат:** дебаты между критиком и адвокатом Tilda
**Оценка Tilda:** 7/10 для задач туристического бизнеса ОАЭ
**Вывод:** Tilda оптимальна для лендингов и каталогов до 50 товаров. Для полноценного e-commerce лучше Shopify. Для блогов -- WordPress.

---

## Инструкции по использованию

### При активации скилла
1. Проверить наличие `experience/_index.md` -- если есть, прочитать критические уроки
2. Для быстрого ответа -- использовать `references/cheatsheet.md`
3. Для детального ответа -- обращаться к соответствующему разделу `SKILL.md`
4. Для специфичных вопросов -- `references/faq.md`
5. Для решения проблем -- `references/troubleshooting.md`

### Когда активировать этот скилл
- Пользователь спрашивает про Tilda, лендинги, конструктор сайтов
- Нужно создать или настроить сайт на Tilda
- Вопросы про формы, API, SEO, платежи в контексте Tilda
- Сравнение Tilda с другими конструкторами
- Настройка интеграций (Telegram, Notion, Stripe) для Tilda-сайта

### При обновлении скилла
1. Обновить версию и дату в SKILL.md и CHANGELOG.md
2. Если добавлен новый раздел -- обновить README.md и этот CLAUDE.md
3. Новые FAQ/проблемы добавлять в соответствующие файлы references/
4. Записывать уроки в `experience/` по протоколу
5. Обновить презентацию при существенных изменениях контента

---

## Технические детали

| Параметр | Значение |
|----------|----------|
| Общий размер скилла | ~69 KB (5 файлов) |
| Слов в SKILL.md | ~5000 |
| Разделов | 14 + дополнительные секции |
| Примеров кода | HTML, CSS, JS, JSON, Bash, JSON-LD |
| Языки контента | Русский (основной), примеры на English |
