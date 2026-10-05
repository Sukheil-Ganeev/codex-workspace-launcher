# YouTube-справочник

Production-ready руководство по YouTube Data API v3 для туристического бизнеса ОАЭ.

## Структура

```
youtube-справочник/
├── SKILL.md                    # Основной файл (3500 слов)
├── README.md                   # Этот файл
├── references/                 # Подробные гайды (~1000 слов каждый)
│   ├── data-api-v3.md
│   ├── upload-videos.md
│   ├── shorts-optimization.md
│   ├── live-streaming.md
│   ├── analytics-api.md
│   ├── monetization.md
│   ├── playlists-management.md
│   └── make-integration.md
├── assets/
│   ├── templates/              # Helper-скрипты
│   │   ├── video-uploader.py
│   │   ├── shorts-uploader.js
│   │   ├── video-metadata-template.json
│   │   └── thumbnail-generator-prompt.txt
│   └── examples/               # Полные примеры с README
│       ├── tour-videos-uploader/
│       ├── shorts-generator/
│       ├── analytics-dashboard/
│       └── live-stream-setup/
├── scripts/                    # Быстрые команды
│   ├── setup-youtube-api.sh
│   ├── upload-video.py
│   ├── upload-short.py
│   └── get-analytics.sh
└── experience/                 # Накопленный опыт
    └── _index.md
```

## Быстрый старт

1. Прочитайте `SKILL.md` — обзор и квоты 2026
2. Настройте OAuth 2.0: `references/data-api-v3.md`
3. Попробуйте Quick Start из `SKILL.md` (20 минут)
4. Изучите примеры: `assets/examples/`

## Требования

- Google Cloud проект с YouTube Data API v3
- OAuth 2.0 credentials (`client_secret.json`)
- YouTube канал
- Python 3.8+ или Node.js 16+

## Ключевые файлы

- **SKILL.md** — главное руководство, начните отсюда
- **references/data-api-v3.md** — полная настройка OAuth 2.0
- **assets/examples/tour-videos-uploader/** — рабочий пример автозагрузки
- **assets/examples/shorts-generator/** — создание Shorts из длинных видео

## Важно

- **Квота:** 10,000 units/день (videos.insert = 1,600 units)
- **YouTube Shorts:** автоопределение <60 сек + вертикальный формат
- **Resumable upload:** обязателен для файлов >5 MB

## Версия

1.0 (05.02.2026)

## Автор

Claude Code Agent для туристического бизнеса ОАЭ (Сухейль)
