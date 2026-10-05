# Instagram-справочник

Production-ready руководство по Instagram как платформе для туристического бизнеса ОАЭ.
Публикации, Reels, Stories, Shopping, Insights, хэштеги, встраивание контента.

> **DM-боты и автоматизация** вынесены в отдельный `instagram-bot-справочник`

## Структура

```
instagram-справочник/
├── SKILL.md                    # Основной файл (~4500 слов)
├── README.md                   # Этот файл
├── references/
│   ├── faq.md                  # 15 частых вопросов
│   ├── troubleshooting.md      # 15 типичных проблем
│   └── cheatsheet.md           # Шпаргалка: endpoints, параметры, метрики
└── experience/
    └── _index.md               # Накопленный опыт
```

## Быстрый старт

1. Прочитайте `SKILL.md` — полный обзор платформы
2. Изучите раздел "Аутентификация" — настройка OAuth 2.0
3. Попробуйте Quick Start (раздел 3: Content Publishing)
4. Настройте аналитику (раздел 7: Insights API)

## Что покрывает справочник

| Раздел | Описание |
|--------|---------|
| Обзор API | Graph API, типы аккаунтов, версионирование |
| Аутентификация | OAuth 2.0, токены, permissions, App Review |
| Content Publishing | Фото, видео, карусели (до 10 медиа) |
| Reels | Публикация, обложки, аналитика, skip_rate |
| Stories | Публикация фото/видео, ограничения стикеров |
| Shopping | Product Tagging, каталог, Commerce Manager |
| Insights | Метрики аккаунта, постов, Stories, Reels, демография |
| Хэштеги | Hashtag Search, Top/Recent Media, стратегия |
| Mentions | Mentioned Media, управление комментариями |
| Broadcast Channels | Обзор, отсутствие API, ручное управление |
| Collaborative Posts | Совместные публикации через API |
| Branded Content | Creator Marketplace, Partnership Ads |
| oEmbed | Встраивание постов (Meta oEmbed Read) |
| Примеры для ОАЭ | Автопостинг, Reels-стратегия, Shopping билетов |
| Rate Limits | 200/час, 25 публикаций/день, хэштеги 30/неделю |

## Требования

- Instagram Business/Creator аккаунт
- Facebook Page (привязанная к Instagram)
- Facebook App с продуктом "Instagram"
- Access Token с необходимыми permissions
- Graph API v22.0+

## Версия

2.0 (12.02.2026)

## Автор

Claude Code Agent для туристического бизнеса ОАЭ (Сухейль)
