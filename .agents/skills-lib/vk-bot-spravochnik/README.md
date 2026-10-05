# VK Bot API: Справочник

Production-ready руководство по созданию ботов ВКонтакте для туристического бизнеса в ОАЭ.

## Структура

```
vk-bot-справочник/
├── SKILL.md              # Основной справочник (~4800 слов)
├── README.md             # Этот файл
└── references/
    ├── faq.md            # 15 частых вопросов
    ├── troubleshooting.md # 15 типичных проблем и решений
    └── cheatsheet.md     # Шпаргалка: методы, параметры, лимиты
```

## Что внутри SKILL.md

| Раздел | Описание |
|--------|----------|
| Quick Start | Создание бота за 5 минут (vkbottle + vk-io) |
| Архитектура | Long Poll vs Callback API — сравнение и выбор |
| Аутентификация | Community / User / Service токены |
| Long Poll API | Подключение, reconnect, обработка ошибок |
| Callback API | Flask/Express серверы, confirmation, events |
| Обработка сообщений | messages.send, вложения, ответы, пересылки |
| Клавиатуры | Reply/Inline, 6 типов кнопок, callback-обработка |
| Карусели | Горизонтальные карточки с фото и кнопками |
| Медиа | Загрузка фото, документов, голосовых |
| State Machine | Многошаговые диалоги, FSM через vkbottle |
| VK Pay | Платежные кнопки, параметры hash |
| VK Mini Apps | Запуск из бота, обмен данными через VK Bridge |
| Рассылки | Разрешения, массовая отправка, лимиты |
| Rate Limits | 20 req/sec, execute (25 вызовов), коды ошибок |
| Примеры | Полный бот-каталог экскурсий ОАЭ |
| Деплой | systemd, pm2, Docker, Serverless (Yandex Cloud) |
| Библиотеки | vkbottle, vk_api, vk-io + другие языки |

## Технологии

- **Python:** vkbottle (async, рекомендуется), vk_api (sync)
- **Node.js:** vk-io (TypeScript, modern)
- **API:** VK API v5.199 (2026)
- **Деплой:** systemd, pm2, Docker, Yandex Cloud Functions

## Применение для бизнеса

- Бот-каталог экскурсий с каруселями
- Автоматическое бронирование через State Machine
- FAQ-бот с обработкой частых вопросов
- Приём платежей через VK Pay
- Рассылки акций подписчикам

## Связанные справочники

- `vk-справочник` — платформа VK (постинг, медиа, сообщества, реклама)
- `telegram-bot-справочник` — боты Telegram
- `whatsapp-bot-справочник` — боты WhatsApp Business API

---

**Версия:** 1.0 | **Дата:** 2026-02-12
