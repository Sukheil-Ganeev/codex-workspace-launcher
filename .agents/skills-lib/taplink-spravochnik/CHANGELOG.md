# Changelog -- taplink-справочник

Все существенные изменения скилла документируются в этом файле.
Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/).

---

## [1.0.0] -- 2026-02-14

### Создано

- **SKILL.md** -- основной справочник (~5000 слов, 14 разделов)
- **README.md** -- навигация и описание структуры
- **CHANGELOG.md** -- история изменений (этот файл)
- **references/faq.md** -- 12 часто задаваемых вопросов с ответами
- **references/troubleshooting.md** -- 12 типичных проблем и решений
- **references/cheatsheet.md** -- шпаргалка (тарифы, блоки, webhook, CSS, UTM, платежи)
- **diagrams/** -- 6 Mermaid-диаграмм:
  - `architecture.md` -- архитектура Taplink
  - `webhook-flow.md` -- поток Webhook-событий
  - `comparison-chart.md` -- сравнение с конкурентами (Linktree, Shorby, Koji)
  - `integration-map.md` -- карта интеграций
  - `tourism-flow.md` -- поток бронирования туризма через Taplink
  - `tariff-comparison.md` -- сравнение тарифов Basic/Pro/Business
- **templates/** -- 7 готовых шаблонов:
  - `taplink-page-tourism.html` -- HTML-шаблон страницы для туризма
  - `webhook-handler.js` -- JS-обработчик Webhook
  - `custom-styles.css` -- CSS-кастомизация
  - `telegram-integration.js` -- JS-интеграция с Telegram
  - `makecom-workflow.json` -- JSON-шаблон для Make.com
  - `payment-setup-guide.md` -- гайд по настройке платежей
  - `whatsapp-button.html` -- HTML-кнопка WhatsApp с CTA
- **Интерактивная HTML презентация** -- 50 слайдов, ~149 KB
- **Проектная папка** -- `D:/Downloads/TAPLINK_СПРАВОЧНИК/` (15 подпапок 00-14, 45 файлов)
- **CLAUDE.md** -- мета-описание скилла

### Процесс создания

- **Команда:** 18 AI-тиммейтов + Team Lead
- **Методология:** 5 волн
  1. Исследование (9 файлов: basics, builder, integrations, payments, api, comparison)
  2. Верификация (критический отчет: 12 противоречий, 52 пункта)
  3. Написание (SKILL.md + references + diagrams + templates)
  4. Презентация (50 слайдов HTML)
  5. QA (финальная проверка)
- **QA результат:** 63/63 проверок PASSED
- **Верификация:** 7 критических ошибок исправлены до публикации

### Применённые коррекции из верификации

- Taplink **НЕ имеет REST API** -- только Webhooks (send-only, 2 события)
- Timer, Forms, CRM -- только тариф **Business** (не Pro)
- Business: макс. $9/мес (квартально), ~$4.50/мес (годовой)
- **НЕТ мобильного приложения** -- управление только через веб
- **11 языков** интерфейса (не 12), арабский НЕ поддерживается
- JivoSite -- только Business (не Basic)
- 300+ тем дизайна, **60+ платёжных провайдеров**, 0% комиссия Taplink

### Ключевые факты

- Taplink НЕ имеет публичного REST API (только Webhooks)
- Timer, Forms, CRM -- только тариф Business
- 60+ платёжных провайдеров, 0% комиссия Taplink
- 11 языков (арабский НЕ поддерживается)
- Основан в 2017 (Австрия), ~8 млн страниц создано
- Mobile-first дизайн, оптимизирован для просмотра со смартфона

### Покрытие разделов

1. Обзор платформы и тарифы
2. Быстрый старт -- мультиссылка за 30 минут
3. Библиотека блоков и конструктор
4. Мини-лендинги и многостраничность
5. Формы, заявки и CRM
6. Webhooks и автоматизация
7. Мессенджеры (WhatsApp, Telegram)
8. Платёжные системы
9. CRM-интеграции
10. Кастомизация (HTML/CSS/JS)
11. Соцсети и трафик
12. SEO и аналитика
13. Практические примеры для ОАЭ
14. Production-чеклист

### Источники

- 9 исследовательских файлов (basics, builder, integrations, payments, api, comparison)
- Критический отчет (critique-report.md) -- 12 противоречий, 52 пункта верификации
- Верификационный отчет (verification-report.md) -- 12 подтверждено, 7 опровергнуто, 6 неверифицируемо
