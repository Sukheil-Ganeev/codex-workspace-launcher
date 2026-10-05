# CHANGELOG -- shopify-справочник

Все значимые изменения в скилле документируются в этом файле.

---

## [1.0.0] -- 2026-02-13

### Initial Release

**Полный справочник по Shopify e-commerce для туристического бизнеса ОАЭ.**

### Созданные файлы

| Файл | Размер | Описание |
|------|--------|----------|
| `SKILL.md` | ~1188 строк, ~5000 слов | Основной справочник, 14 разделов |
| `README.md` | ~58 строк | Структура проекта, быстрый старт |
| `references/faq.md` | ~303 строки | 12 часто задаваемых вопросов |
| `references/troubleshooting.md` | ~377 строк | 12 типичных проблем и решений |
| `references/cheatsheet.md` | ~425 строк | CLI, API, Liquid, Webhooks, тарифы |
| `CLAUDE.md` | мета-описание | Полная карта скилла |
| `CHANGELOG.md` | этот файл | История изменений |

### Источники исследования

В процессе создания были проверены через WebSearch и WebFetch:
- shopify.dev -- официальная документация (API, Liquid, Themes, CLI)
- shopify.dev/docs/api/admin-graphql -- GraphQL Admin API reference
- shopify.dev/docs/api/liquid -- Liquid template language
- shopify.com/pricing -- актуальные тарифы (февраль 2026)
- Shopify Payments supported countries -- подтверждение отсутствия ОАЭ
- Stripe, Telr, PayTabs -- альтернативные платёжные шлюзы для ОАЭ
- Shopify App Store -- актуальные приложения для бронирования, отзывов, WhatsApp
- Hydrogen/Oxygen documentation -- headless commerce framework
- Schema.org TouristTrip -- структурированные данные для туризма
- UAE VAT/DTCM requirements -- регуляторные требования

### Валидация

- **Оценка critic-tester:** 9/10
- **Комментарий:** Полный охват Shopify для туристического бизнеса. Все разделы содержат практические примеры с привязкой к ОАЭ. Код готов к использованию. Рекомендации по тарифам и Apps актуальны.

### Ключевые находки исследования (10 пунктов)

1. **Shopify Payments НЕ доступен в ОАЭ** (на февраль 2026) -- ключевое ограничение. Сторонние шлюзы обязательны, плюс доп. комиссия Shopify 0.6-2%
2. **GraphQL API обязателен** -- с апреля 2025 новые public apps не могут использовать REST API. REST считается legacy с октября 2024
3. **Тарифы 2026** -- Starter $5, Basic $39, Grow $105 (бывший Shopify plan), Advanced $399, Plus от $2300. Grow переименован (ранее назывался "Shopify")
4. **Shopify Flow** -- доступен только от плана Grow ($105/мес), критичен для автоматизации (Telegram уведомления, VIP-теги, авто-отмена). Для Basic нужен Zapier/Make
5. **Hydrogen + Oxygen** -- headless React framework от Shopify с бесплатным хостингом. Идеально для кастомного UI бронирования
6. **Мультиязычность** -- до 20 языков на одном магазине через Markets. Translate & Adapt -- бесплатное приложение от Shopify. Dawn поддерживает RTL из коробки
7. **Schema.org TouristTrip** -- специальный тип разметки для туристических услуг, улучшает отображение в Google
8. **Booking apps** -- Shopify не имеет встроенного календаря. BookThatApp ($15/мес) и Sesami (бесплатный tier) -- лучшие варианты для выбора даты/времени
9. **Webhooks** -- таймаут 5 сек, 19 ретраев за 48 часов, затем автоудаление подписки. Обязательно возвращать 200 быстро, обрабатывать асинхронно
10. **VAT 5% ОАЭ** -- рекомендуется включать в цену (include tax in prices). Нужен TRN (Tax Registration Number) и DTCM permit для легальной онлайн-торговли экскурсиями

### Презентация

| Параметр | Значение |
|----------|---------|
| **Тема дизайна** | "Commerce Grid" |
| **Цветовая палитра** | Тёмная (#0E1629) + Shopify Green (#95BF47) + Indigo (#5C6AC4) + Teal (#00A0AC) |
| **Шрифты** | Space Grotesk + Inter + JetBrains Mono |
| **HTML** | `D:/Downloads/Skill_Presentations/shopify/presentation.html` (88 KB) |
| **PDF** | `D:/Downloads/Skill_Presentations/shopify/output/shopify.pdf` (7.7 MB) |
| **Слайдов** | 18 |
| **Формат** | 1920x1080 |

### Команда создания

| Роль | Задача |
|------|--------|
| **researcher-shopify** | Исследование Shopify API, тарифов, Apps, платежей ОАЭ |
| **presenter-shopify** | Создание презентации "Commerce Grid" (18 слайдов) |
| **critic-tester** | Валидация контента, оценка полноты и актуальности |
| **debugger-polisher** | Финальная полировка, исправление ошибок |
