# instagram-bot-справочник

Production-ready руководство по Instagram Messenger API для DM-автоматизации в туристическом бизнесе ОАЭ.

## Что это

Справочник по созданию чат-ботов для Instagram DM через **Messenger API for Instagram** (часть Meta Platform). Instagram не имеет классического Bot API — вся автоматизация работает через Graph API и Webhook-ы.

## Структура

```
instagram-bot-справочник/
├── SKILL.md                    # Основной справочник (полный гайд)
├── README.md                   # Этот файл
└── references/
    ├── faq.md                  # 15 частых вопросов
    ├── troubleshooting.md      # 15 типичных проблем и решений
    └── cheatsheet.md           # Шпаргалка (endpoints, payloads, лимиты)
```

## Ключевые темы

| Раздел | Описание |
|--------|----------|
| Quick Start | Настройка Meta App, подключение IG Business, первый автоответ |
| Архитектура | Messenger API vs FB Messenger, поток данных, webhook events |
| Аутентификация | Page Access Token, Instagram Business Account ID |
| Отправка сообщений | Text, image, video, audio, file |
| Интерактивные элементы | Quick Replies, Generic Template, Ice Breakers, Persistent Menu |
| Private Replies | Автоответ в DM на комментарий к посту |
| Story Mentions | Обработка упоминаний в Stories |
| Human Agent Handover | Передача диалога живому оператору |
| Состояния диалога | FSM для сложных сценариев (бронирование) |
| Модерация | Автоскрытие/удаление спам-комментариев |
| Rate Limits | 200 API вызовов/час, 24-часовое окно, лимиты медиа |

## Критические ограничения

- Нельзя писать первым — бот отвечает только на действия пользователя
- Нет массовых рассылок (broadcast)
- 24-часовое окно для ответов (Human Agent Tag продлевает до 7 дней)
- 200 API вызовов в час на аккаунт
- Только Business/Creator аккаунты

## Связанные справочники

- `instagram-справочник` — контент-публикации, Reels, Stories, аналитика (Graph API)
- `whatsapp-bot-справочник` — боты WhatsApp Business API
- `telegram-bot-справочник` — боты Telegram Bot API
- `vk-bot-справочник` — боты VK Bot API

## Версия

- **v1.0** — 12.02.2026
- **API версия:** Graph API v21.0
- **Автор:** Claude Code Agent
