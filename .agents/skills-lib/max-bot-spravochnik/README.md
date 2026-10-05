# max-bot-справочник

Production-ready руководство по Max (ex-TamTam) Bot API для туристического бизнеса ОАЭ.

## Структура

```
max-bot-справочник/
├── SKILL.md              # Основной справочник (16 разделов)
├── README.md             # Этот файл
└── references/
    ├── faq.md            # Часто задаваемые вопросы
    ├── troubleshooting.md # Решение проблем
    └── cheatsheet.md     # Шпаргалка: endpoints, типы, лимиты
```

## Что внутри

### SKILL.md — основной справочник
1. Quick Start — регистрация через @MasterBot, токен, первый запрос
2. Архитектура — REST API, Long Poll, Webhooks
3. Аутентификация — Authorization header (НЕ query param)
4. Обработка сообщений — GET /updates, POST /messages, типы событий
5. Клавиатуры — InlineKeyboardAttachment, callback/link/contact/geo кнопки
6. Медиа — 3-шаговая загрузка (photo, video, audio, file), геолокация, контакт
7. Карусели — ShareAttachment с карточками
8. Управление чатами — CRUD, участники, типы чатов
9. Long Polling — GET /updates с маркером
10. Webhooks — POST /subscriptions, HTTPS
11. FSM — состояния диалога
12. No-code конструктор — визуальный конструктор Max
13. Rate Limits — 30 RPS, коды ошибок, обработка
14. Примеры для туризма ОАЭ — каталог, бронирование, контакты
15. Деплой — Python, Node.js, Go, Java, PHP, Docker
16. Библиотеки — официальные SDK + сторонние

### references/
- **faq.md** — 15+ вопросов-ответов
- **troubleshooting.md** — типичные проблемы и решения
- **cheatsheet.md** — быстрая шпаргалка по всему API

## Ключевые отличия от старого max-справочника

| Аспект | max-справочник (старый) | max-bot-справочник (новый) |
|--------|------------------------|---------------------------|
| API | VK Bot API (ошибка!) | Max Bot API (platform-api.max.ru) |
| Base URL | api.vk.com | platform-api.max.ru |
| Auth | access_token в URL | Authorization header |
| Scope | Всё (платформа + боты) | Только Bot API |
| Регистрация | Через VK сообщество | Через @MasterBot |

## Версия

- **v2.0.0** — Февраль 2026
- Базируется на актуальном Max Bot API (platform-api.max.ru)
- Примеры для туризма ОАЭ (Дубай)
