# CHANGELOG -- tilda-справочник

Все изменения скилла документируются в этом файле.

---

## [1.0.0] -- 2026-02-13

### Initial Release

Первый полный релиз справочника по Tilda для туристического бизнеса ОАЭ.

### Созданные файлы

| Файл | Размер | Описание |
|------|--------|----------|
| `SKILL.md` | 39 KB | Основной справочник, 14 разделов, ~5000 слов |
| `README.md` | 3 KB | Описание структуры, навигация, быстрый старт |
| `references/faq.md` | 9 KB | 12 частых вопросов с ответами |
| `references/troubleshooting.md` | 10 KB | 12 проблем с решениями |
| `references/cheatsheet.md` | 7 KB | Шпаргалка: блоки, API, CSS, JS, SEO |
| **Итого** | **~69 KB** | **5 файлов** |

### Источники исследования

- Официальная документация Tilda: help.tilda.cc
- Tilda API: help.tilda.cc/api
- Tilda Education: tilda.education
- Zero Block: zero.tilda.cc
- Тарифы: tilda.cc/pricing
- Stripe Documentation для ОАЭ
- Schema.org TouristTrip спецификация
- Google Rich Results Test
- Make.com / Zapier документация
- Weglot документация

### Валидация

- **Оценка:** 8/10 от critic-tester
- **Критическая ошибка найдена и исправлена:** Telegram-интеграция описывала использование @BotFather, что неправильно. Tilda использует собственного бота **@TildaFormsBot** для приёма лидов из форм. Исправлено во всех файлах (SKILL.md, faq.md, troubleshooting.md).
- **Дополнения после валидации:** добавлены ограничения экспорта кода (SSL отключается, шрифты требуют подписки, формы перестают работать, CRM/Members/Catalog не экспортируются, защита паролем отключается).

### Ключевые находки

- Tilda оптимальна для лендингов и каталогов до 50 товаров ($15-25/мес)
- Для полноценного e-commerce (>50 товаров, инвентарь, подписки) лучше Shopify
- Telegram-интеграция через @TildaFormsBot (НЕ @BotFather) -- специальный бот Tilda
- API только на Business плане, жёсткий лимит 150 req/hr
- В ОАЭ из платёжных систем Tilda работают: Stripe, PayPal, 2Checkout
- CloudPayments, ЮKassa, Robokassa -- только для РФ/СНГ, не работают в ОАЭ
- Zero Block позволяет создавать уникальные блоки с точностью до пикселя (5 breakpoints)
- Мультиязычность: отдельные проекты (Business) или папки (Personal), автоперевод Weglot $15+/мес
- CDN Tilda: 5500 серверов, 100+ точек присутствия, 99.9% uptime

### Презентация "Canvas Flow"

| Параметр | Значение |
|----------|----------|
| **HTML** | `D:/Downloads/Skill_Presentations/tilda/presentation.html` |
| **PDF** | `D:/Downloads/Skill_Presentations/tilda/output/tilda.pdf` |
| **Тема** | "Canvas Flow" -- светлая тема с warm coral палитрой |
| **Размер HTML** | 84 KB |
| **Размер PDF** | 4.5 MB |
| **Слайдов** | 18 |
| **Шрифты** | Plus Jakarta Sans, DM Sans, Fira Code |
| **Палитра** | coral #FF7B54, purple #6E56CF, teal #2A9D8F, warm coral #E76F51 |

**Слайды:**
01. Титульный (hero)
02. Содержание
03. Блоковая система Tilda
04. Планы и цены (2026)
05. Библиотека блоков
06. Zero Block -- визуальный редактор
07. Типографика и стили
08. Анимации и эффекты
09. Формы и сбор лидов
10. Tilda API
11. SEO в Tilda
12. Tilda Store (магазин)
13. Структура лендинга
14. Мультиязычность (RU/EN/AR)
15. Интеграции
16. HTML / CSS / JS в Tilda
17. Tilda vs Конкуренты
18. Чек-лист публикации

### Исследование альтернатив

- **Охват:** 15 конструкторов сайтов (Tilda, Shopify, WordPress, Wix, Squarespace, Webflow, Framer, Notion Sites, Carrd, Readymag, Figma Sites, Duda, GoDaddy, Weebly, Strikingly)
- **Формат:** Дебаты: критик (против Tilda) vs адвокат (за Tilda)
- **Итоговая оценка Tilda:** 7/10 для задач туристического бизнеса ОАЭ
- **Вывод:** Tilda -- лучший выбор для лендингов и небольших каталогов. Shopify -- для масштабного e-commerce. WordPress -- для контентных сайтов и блогов.

### Дополнительная презентация "Navigator"

| Параметр | Значение |
|----------|----------|
| **Тема** | "Navigator" -- навигация по альтернативам |
| **Размер HTML** | 77 KB |
| **Слайдов** | 15 |
| **Размер PDF** | 6.0 MB |

### Команда создания

| Агент | Роль |
|-------|------|
| **researcher-tilda** | Исследование платформы, API, интеграций, сбор данных |
| **presenter-tilda** | Создание презентации "Canvas Flow" (18 слайдов) |
| **critic-tester** | Валидация справочника, оценка 8/10, нахождение критических ошибок |
| **debugger-polisher** | Исправление ошибок (@TildaFormsBot), дополнение ограничений экспорта |
| **researcher-alternatives** | Исследование 15 конструкторов-альтернатив |
| **debate-critic** | Дебаты: аргументы против Tilda, слабые стороны |
| **debate-advocate** | Дебаты: аргументы за Tilda, сильные стороны для туризма |

---

## Формат записей

Каждая запись содержит:
- Версию и дату
- Список изменений (Added / Changed / Fixed / Removed)
- Размеры файлов
- Ключевые находки и уроки
