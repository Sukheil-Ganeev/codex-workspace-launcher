# voicebot-справочник

**Навигатор-справочник по проекту VoiceTranscriptionBot** -- голосовой бот для туристического бизнеса в ОАЭ (Дубай).

## Назначение

Компактный скилл-навигатор для быстрого поиска информации о проекте VoiceTranscriptionBot:
- Архитектура пайплайна (Audio -> STT -> LLM -> DB)
- Все команды Telegram (30) и WhatsApp (35+) и Admin (47+)
- 9 бизнес-категорий и маршрутизация по команде
- LLMClient и TaskType routing (CLASSIFICATION, ANALYSIS, CREATIVE, TRANSFORMATION, VISION, PLANNING)
- Модули (~60 core + 17 bot + 14 admin), env-переменные, схемы БД
- Безопасность (HMAC, whitelist, approval, log sanitizer, антиспам)
- Deploy (Oracle ARM, systemd, nginx, Docker, CI/CD)

## Версия проекта

**v6.1.0** | Python 3.13 | aiogram 3.x + FastAPI | ~2138 tests

## Расположение проекта

`D:/Downloads/VoiceTranscriptionBot/`

## Структура скилла

```
voicebot-справочник/
├── SKILL.md                          # Главный навигатор (~5000 слов)
├── README.md                         # Этот файл
├── references/
│   ├── stt-pipeline.md               # STT cascade, Transcriber, Whisper, Groq, diarization
│   ├── llm-cascade.md                # LLMClient, TaskType, Gemini models, correction, sentiment, summary, improver
│   ├── business-modules.md           # Категории, OCR, клиенты, команда, прайс, уроки, калькулятор, маршруты
│   ├── telegram-commands.md          # 30 команд, callbacks, keyboards, middleware, FSM
│   ├── whatsapp-commands.md          # 35+ команд, buttons, lists, reactions
│   ├── infrastructure.md             # DB schema, export, formatter (6 модулей), scheduler, healthcheck, backup
│   ├── security.md                   # HMAC, whitelist, approval, log sanitizer, admin security, nginx, deploy
│   ├── cheatsheet.md                 # Быстрые рецепты
│   ├── troubleshooting.md            # Решение проблем
│   └── faq.md                        # Часто задаваемые вопросы
├── experience/
│   └── _index.md                     # Критические уроки (9 уроков)
├── assets/                           # Шаблоны и примеры (при наличии)
└── scripts/                          # Скрипты автоматизации (при наличии)
```

## Активация скилла

**Ключевые слова:**
- `voicebot`, `голосовой бот`, `транскрипция`
- `whisper`, `STT`, `voice transcription`
- `VoiceTranscriptionBot`, `voice pipeline`
- `распознавание речи`, `голосовые сообщения`
- `admin bot`, `админ-бот`, `task routing`
- `llm client`, `TaskType`, `LLMClient`

## Как пользоваться

1. SKILL.md -- для быстрого поиска: команды, модули, env, категории, TaskType routing
2. references/ -- для детального погружения в конкретную тему
3. experience/ -- для критических уроков из прошлого опыта

## Источники данных

Скилл построен на основе 5 research-документов:
- `_research/research-core-pipeline.md` -- Core Voice Pipeline Architecture
- `_research/research-telegram-bot.md` -- Telegram Bot Technical Research
- `_research/research-whatsapp-security-deploy.md` -- WhatsApp, Security & Deployment
- `_research/research-business-modules.md` -- Business Logic Modules
- `_research/research-infrastructure.md` -- Infrastructure (DB, Export, Formatter, Scheduler)
