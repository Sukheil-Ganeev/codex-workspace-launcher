# WhatsApp Bot / Business API Справочник

## Назначение

Production-ready руководство по разработке WhatsApp-ботов через официальный Cloud API (Meta).
Заменяет `whatsapp-business-api-справочник` и дополняет `whatsapp-справочник`.

## Для кого

- Разработчики, создающие WhatsApp-ботов для туристического бизнеса ОАЭ
- Предприниматели, интегрирующие WhatsApp Business API в свои системы

## Структура

```
whatsapp-bot-справочник/
├── SKILL.md              # Основной справочник (~4800 слов, 16 разделов)
├── README.md             # Этот файл
└── references/
    ├── faq.md            # 15 частых вопросов
    ├── troubleshooting.md # 15 типичных проблем и решений
    └── cheatsheet.md     # Шпаргалка: endpoints, коды ошибок, лимиты
```

## Когда активировать

- Запрос на создание WhatsApp-бота
- Вопросы по WhatsApp Cloud API / Business API
- Настройка webhooks, шаблонов (HSM), Flows
- Интеграция WhatsApp с CRM, Notion, Google Sheets
- Вопросы по ценообразованию WhatsApp API
- Работа с интерактивными элементами (кнопки, списки, каталоги)

## Ключевые разделы SKILL.md

1. Quick Start (15 минут до первого сообщения)
2. Архитектура (Cloud API, BSP)
3. Аутентификация (System User Token, App Secret)
4. Типы сообщений (text, image, video, document, audio, sticker, location, contacts, reaction)
5. Интерактивные элементы (buttons, lists, CTA, products)
6. Шаблоны HSM (создание, категории, отправка)
7. WhatsApp Flows (интерактивные формы)
8. Webhooks (verification, обработка, подпись)
9. Состояния диалога (FSM)
10. Каталог продуктов (Commerce API)
11. Ценообразование 2025-2026
12. Rate Limits и качество
13. Примеры для туризма ОАЭ
14. Деплой (Node.js, Python, Serverless)
15. Интеграции (Google Sheets, Notion, Make.com)
16. Библиотеки и SDK

## Актуальность

- API версия: v21.0
- Ценовая модель: per-message (с 1 июля 2025)
- Tier-система: упрощённая (250 → 100K → Unlimited) с Q1-Q2 2026
- On-Premise API: закрыт (октябрь 2025)
- Последнее обновление: 12.02.2026
