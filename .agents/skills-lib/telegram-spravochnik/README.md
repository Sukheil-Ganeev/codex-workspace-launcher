# Telegram Platform — Production Справочник

Production-ready руководство по платформе Telegram для туристического бизнеса ОАЭ.
Каналы, группы, контент, аналитика, реклама, Premium, Business, Mini Apps, MTProto/TDLib.

> Боты: см. `telegram-bot-справочник` — отдельный справочник по Telegram Bot API

## Структура справочника

```
telegram-справочник/
├── SKILL.md                          # Главный файл (~4500 слов)
├── README.md                         # Этот файл
├── references/                       # Детальные гайды
│   ├── faq.md                       # 15 вопросов о платформе
│   ├── troubleshooting.md           # 15 проблем и решений
│   └── cheatsheet.md                # Методы, лимиты, шпаргалка
└── experience/                       # База знаний
    └── _index.md
```

## Что покрывает этот справочник

1. **API-уровни** — MTProto vs Bot API vs TDLib, выбор для задачи
2. **Аутентификация** — API ID/Hash, сессии, 2FA
3. **Каналы** — создание, публикация, медиагруппы, планирование
4. **Группы** — супергруппы, топики, модерация, slow mode
5. **Контент** — форматирование, лимиты медиа, кастомные эмодзи
6. **Stories** — публикация, виджеты, поиск по хэштегам
7. **Premium** — лимиты, стоимость, бизнес-выгода
8. **Business** — бизнес-профиль, автоответы, Quick Replies
9. **Ads** — рекламная платформа, CPM, таргетинг
10. **Mini Apps** — Stars, полноэкранный режим, подписки
11. **Аналитика** — встроенная, TGStat, ERR, охват
12. **Библиотеки** — Telethon, Pyrogram, GramJS, TDLib
13. **Модерация** — права, антиспам, безопасность
14. **Туризм ОАЭ** — автопостинг, мониторинг, контент-план
15. **Rate Limits** — FloodWait, лимиты MTProto

## Что НЕ покрывает (см. telegram-bot-справочник)

- Bot API методы (sendMessage, getUpdates и т.д.)
- BotFather, создание и настройка ботов
- Webhooks и Long Polling для ботов
- Inline-кнопки и callback queries
- Telegram Payments через Bot API
- Web Apps (ботовая часть)
- Деплой ботов

## Быстрый старт

1. Прочитайте `SKILL.md` — полное руководство
2. Для конкретных вопросов — `references/faq.md`
3. Для решения проблем — `references/troubleshooting.md`
4. Шпаргалка по методам — `references/cheatsheet.md`

## Ключевые библиотеки

- **Telethon** (Python): https://docs.telethon.dev — рекомендуемый
- **Pyrogram** (Python): https://docs.pyrogram.org — альтернатива
- **TDLib** (C++): https://github.com/tdlib/td — официальная от Telegram

## Кейсы для туризма ОАЭ

- Автопостинг каталога экскурсий в канал
- Мониторинг упоминаний в туристических группах
- Недельная контент-стратегия канала
- Аналитика аудитории через TGStat

**Версия:** 2.0
**Дата:** 12.02.2026
