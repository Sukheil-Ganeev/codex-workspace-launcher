---
id: EXP-002
date: 2026-02-17
type: fix
severity: critical
tags: [docker-pricing, critic-errors, verification]
---

## Проблема

Критик указал "правильные" цены Docker Desktop $7/$11/$21 -- это оказались УСТАРЕВШИЕ данные (до декабря 2024).

## Контекст

Актуальные цены (с декабря 2024):
- **Pro:** $9/мес (annual)
- **Team:** $15/мес (annual)
- **Business:** $24/мес (annual)

Старые цены $7/$11/$21 встречаются во многих статьях и форумах, но Docker обновил прайсинг.

## Решение

Advocate-verification подтвердила данные из research, опровергла критика. Правило: ВСЕГДА проверять цены на официальном сайте docker.com/pricing, а не в блогах/форумах.

## Урок

Критические замечания критика ТОЖЕ нужно верифицировать. Процесс: researcher -> critic -> advocate-verification -> writer. Advocate -- последний фильтр перед записью.
