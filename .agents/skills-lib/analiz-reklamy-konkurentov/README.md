# Анализ рекламы конкурентов

Скилл для Claude Code: систематический анализ рекламных кампаний конкурентов в туристическом бизнесе ОАЭ.

## Что делает

- Собирает активные рекламные объявления конкурентов с 4 платформ
- Анализирует креативы, тексты, УТП, таргетинг, ценовое позиционирование
- Сравнивает конкурентов между собой и с нашим бизнесом
- Находит незанятые ниши и пробелы рынка
- Генерирует отчёт с actionable рекомендациями

## Платформы

| Платформа | Метод | Покрытие |
|-----------|-------|----------|
| Meta (FB/IG) | Ad Library API через MCP (без токена) | Полное |
| Google/YouTube | Ads Transparency Center | Полное |
| ВКонтакте | WebSearch + WebFetch (ручной) | Частичное |
| Яндекс.Директ | Wordstat + ручной анализ выдачи | Частичное |

## Команды

```
/adspy meta [конкурент]              -- Facebook/Instagram
/adspy google [конкурент]            -- Google Ads/YouTube
/adspy vk [конкурент или запрос]     -- ВКонтакте
/adspy yandex [ключевое слово]       -- Яндекс.Директ
/adspy all [конкурент]               -- все 4 платформы
/adspy compare [конкурент1, конкурент2, ...]  -- сравнение
```

## Структура

```
анализ-рекламы-конкурентов/
├── SKILL.md              -- главный файл скилла (оркестратор)
├── README.md             -- это описание
├── agents/               -- субагенты по платформам
│   ├── meta-spy.md       -- Meta Ad Library (MCP, 5 фаз)
│   ├── google-spy.md     -- Google Transparency Center (5 фаз)
│   ├── vk-spy.md         -- ВКонтакте ручной анализ (5 фаз)
│   └── yandex-spy.md     -- Яндекс.Директ + Wordstat (6 фаз)
├── references/           -- справочные материалы
│   ├── uae-tourism.md    -- контекст бизнеса, конкуренты, сезонность
│   ├── platforms.md      -- что анализировать на каждой платформе
│   └── report-template.md -- шаблон финального отчёта
└── assets/
    └── tourism-template.md
```

## MCP-серверы

| MCP | Назначение | Токен |
|-----|-----------|-------|
| `facebook-ads-library-mcp` (trypeggy) | Meta Ad Library | Не нужен |
| `google-ads-transparency` (talknerdytome) | Google Transparency | Не нужен |

## Источники (исследование)

Основано на: `D:/Downloads/исследование_скиллов_анализ_рекламы_конкурентов.md`

Ключевые open-source инструменты:
- `facebook-ads-library-mcp` (trypeggy, 191 stars) -- Meta без токена
- `google-ads-transparency` (talknerdytome) -- Google без токена
- `claude-ads` (AgriciDaniel, 876 stars) -- структура аудита
- 9 n8n workflow для автоматизации

## Вывод

Отчёты сохраняются в: `D:/Downloads/Chats/_база/md/competitor-ads-analysis-YYYY-MM-DD.md`
