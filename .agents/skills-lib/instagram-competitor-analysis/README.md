# Instagram Competitor Analysis Skill

## Overview

Systematic framework for helping users choose and implement Instagram competitor monitoring solutions.

## What This Skill Does

Provides decision framework for selecting between 3 approaches:
1. **Free** (Python + Instaloader) - $0, 1-10 competitors
2. **Cloud** (Apify/Phantom Buster) - $50-150/mo, 10-50 competitors
3. **AI-Powered** (Full automation + Claude) - $100+/mo, 50+ competitors

## When Claude Uses This Skill

Automatically triggers when users mention:
- Instagram competitor tracking
- Automating social media monitoring
- Scraping competitor posts
- Instagram data extraction
- Comparing Instagram analysis tools

## Testing Results

**TDD Phase:** RED-GREEN-REFACTOR completed

**Baseline (without skill):**
- ✅ Agents asked clarifying questions
- ❌ No systematic decision framework
- ❌ Technical jargon without translation
- ❌ No reference to existing solutions

**With skill:**
- ✅ Follows decision flowchart
- ✅ Progressive disclosure (doesn't overwhelm)
- ✅ Translates technical terms
- ✅ References D:/Downloads project
- ✅ Sets realistic expectations

**Compliance:** 5/5 criteria passed

## Integration

**References existing project:**
- `D:/Downloads/instagram_competitor_analysis/`
  - Complete implementations for all 3 approaches
  - Ready-to-use Python scripts
  - API clients
  - Documentation

Skill points users to existing code instead of recreating.

## Structure

```
instagram-competitor-analysis/
├── SKILL.md                        # Main reference guide
├── README.md                       # This file
├── experience/                     # Накопленный опыт
│   ├── _index.md                   # Топ-5 критических уроков (ЧИТАТЬ!)
│   ├── fixes/                      # Исправленные ошибки
│   │   └── instagram-tos-warning-missing.md
│   ├── improvements/               # Найденные улучшения
│   │   └── progressive-disclosure-pattern.md
│   ├── patterns/                   # Повторяющиеся паттерны
│   │   └── clarification-before-solution.md
│   └── warnings/                   # Что НЕ делать
│       └── dont-recreate-existing-code.md
└── references/                     # Справочные материалы
    ├── faq.md                      # Часто задаваемые вопросы (5 вопросов)
    ├── troubleshooting.md          # Решение проблем (3 типичные проблемы)
    └── cheatsheet.md               # Шпаргалка (команды, паттерны, лимиты)
```

**При активации скилла:** ОБЯЗАТЕЛЬНО читать `experience/_index.md` — критические уроки из тестирования!

## Skill Type

**Reference** - Provides decision framework and tool comparison guide

Not a process skill (like TDD) - no enforcement needed, just guidance.

## Keywords

Instagram scraping, competitor monitoring, Instaloader, Apify, Phantom Buster, Instagram API, social media intelligence, competitor analysis automation, Instagram business intelligence

## Created

2024-02-05

## Testing Method

Used TDD approach:
1. RED: Ran 3 pressure scenarios without skill
2. GREEN: Created skill addressing baseline failures
3. REFACTOR: No new rationalizations found (agents already well-behaved)

## Notes

Baseline agents were already asking clarifying questions (good behavior). Skill adds systematic framework they were missing, not discipline enforcement.

## Experience System

**При каждой активации скилла:**
1. Читать `experience/_index.md` → Топ-5 критических уроков
2. Применять паттерны из `experience/patterns/`
3. Избегать ошибок из `experience/warnings/`

**Добавление нового опыта:**
- Исправлена ошибка? → `experience/fixes/название.md`
- Найдено улучшение? → `experience/improvements/название.md`
- Выявлен паттерн? → `experience/patterns/название.md`
- Обнаружена проблема? → `experience/warnings/название.md`

Затем обновить `experience/_index.md` если урок критичный (входит в топ-5).
