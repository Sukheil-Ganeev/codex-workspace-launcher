# DOCS OPTIMIZER — FRESHNESS REPORT
**Mode:** `freshness check`
**Project:** TouristBotEcosystem (`D:/Downloads/TouristBotEcosystem/`)
**Date:** 2026-03-12
**Verification Score:** 2/5

---

## PHASE 1: DISCOVERY — FILE FRESHNESS METRICS

Метод: `git log --format="%ad" --date=short -1 -- <file>` для каждого .md файла.

| Файл | Последнее обновление | Дней назад | Строк | ~Токенов | Статус |
|------|---------------------|------------|-------|----------|--------|
| CHANGELOG.md | 2026-03-05 | 7 | 1 088 | 4 352 | active |
| CLAUDE.md | 2026-03-05 | 7 | 557 | 2 228 | active |
| ISSUES.md | 2026-03-04 | 8 | 110 | 440 | active |
| MASTER_PLAN.md | 2026-03-03 | 9 | 1 900 | 7 600 | active — содержит устаревшие статусы |
| README.md | 2026-03-04 | 8 | 351 | 1 404 | active |
| deploy/README.md | 2026-03-03 | 9 | 71 | 284 | active |
| docs/ARCHITECTURE.md | 2026-03-03 | 9 | 424 | 1 696 | **CONTENT-STALE** — v4.0 при текущей v5.9.0 |
| docs/ARCHITECTURE_v1.md | 2026-03-03 | 9 | 841 | 3 364 | archive snapshot — OK |
| docs/AUDIT_2026-03-03.md | 2026-03-03 | 9 | 332 | 1 328 | archive (Phase 0) — OK |
| docs/audit_ai_lessons.md | 2026-03-03 | 9 | 210 | 840 | archive — OK |
| docs/audit_business.md | 2026-03-03 | 9 | 136 | 544 | archive — OK |
| docs/audit_content.md | 2026-03-03 | 9 | 119 | 476 | archive — OK |
| docs/audit_ecosystem.md | 2026-03-03 | 9 | 182 | 728 | archive — OK |
| docs/audit_infra.md | 2026-03-03 | 9 | 178 | 712 | archive — OK |
| docs/audit_voice.md | 2026-03-03 | 9 | 123 | 492 | archive — OK |
| docs/BUTTON_DESIGN_GUIDE.md | 2026-03-04 | 8 | 1 039 | 4 156 | active |
| docs/CICD_SETUP.md | 2026-03-04 | 8 | 105 | 420 | active |
| docs/CODE_REVIEW_v1.md | 2026-03-03 | 9 | 385 | 1 540 | archive snapshot — OK |
| docs/COMMAND_AUDIT.md | 2026-03-04 | 8 | 218 | 872 | **CONTENT-STALE** — Batch 5, не покрывает /expenses, /report |
| docs/COMMAND_AUDIT_ADMIN.md | 2026-03-04 | 8 | 262 | 1 048 | **CONTENT-STALE** — v5.3.0, inline callbacks v5.9.0 не отражены |
| docs/DATABASE_COVERAGE_AUDIT.md | 2026-03-04 | 8 | 337 | 1 348 | active |
| docs/DEPLOY.md | 2026-03-03 | 9 | 798 | 3 192 | **CONTENT-STALE** — Oracle Cloud, проект на GCP |
| docs/DEPLOY_GCP.md | 2026-03-03 | 9 | 1 062 | 4 248 | active (актуальный) |
| docs/DEPLOY_LESSONS_2026-03-03.md | 2026-03-03 | 9 | 166 | 664 | archive (dated) — OK |
| docs/IDEAL_MASTER_PLAN.md | — (untracked) | N/A | 2 559 | 10 236 | untracked — нет git истории |
| docs/IMPROVEMENT_MASTER_PLAN.md | 2026-03-04 | 8 | 879 | 3 516 | **CONTENT-STALE** — помечен ACTIVE, но закрыт в v5.7.0 |
| docs/IMPROVEMENT_MASTER_PLAN_v2.md | 2026-03-04 | 8 | 255 | 1 020 | active |
| docs/MANUAL_TESTS.md | 2026-03-03 | 9 | 321 | 1 284 | **CONTENT-STALE** — v4.3.0, нет /expenses, /report, /areas |
| docs/plans/2026-03-02-merge-vtb-cf-plan.md | 2026-03-02 | 10 | 961 | 3 844 | archive (завершён план) — OK |
| docs/plans/2026-03-02-unified-telegram-bot.md | 2026-03-02 | 10 | 990 | 3 960 | archive (завершён план) — OK |
| docs/PROJECT_ACCOMPLISHMENTS.md | 2026-03-04 | 8 | 628 | 2 512 | active snapshot |
| docs/SENTRY_GUIDE.md | 2026-03-04 | 8 | 187 | 748 | active |
| docs/SERVER_HEALTH_REPORT_2026-03-04.md | 2026-03-04 | 8 | 142 | 568 | dated report — OK |
| docs/SERVER_RUNBOOK.md | 2026-03-04 | 8 | 361 | 1 444 | active |
| docs/USER_GUIDE_admin.md | 2026-03-03 | 9 | 390 | 1 560 | **CONTENT-STALE** — v1.0, Admin redesign не отражён |
| docs/USER_GUIDE_owner.md | 2026-03-03 | 9 | 476 | 1 904 | **CONTENT-STALE** — нет /expenses, /report |
| docs/USER_GUIDE_staff.md | 2026-03-03 | 9 | 145 | 580 | **CONTENT-STALE** — нет /expenses, /report |
| docs/UX_DESIGN_v1.md | 2026-03-03 | 9 | 1 103 | 4 412 | archive snapshot — OK |
| docs/WHATSAPP_BOT_REDESIGN.md | 2026-03-04 | 8 | 522 | 2 088 | active |

---

## PHASE 2: FRESHNESS ANTI-PATTERN ANALYSIS

### Обнаруженные AP-F0X нарушения

```
AP-F02 | docs/ARCHITECTURE.md | Версия v4.0 в тексте, текущая v5.9.0 — расхождение 1 мажорная версия | Severity: HIGH
AP-F04 | docs/ARCHITECTURE.md | Описывает 5 ботов, 13 handlers, Phase 0 + Batch 1-4 — реально 3 бота, Batch 5-6 не отражены | Severity: HIGH
AP-F02 | docs/MANUAL_TESTS.md | Указана версия v4.3.0+, текущая v5.9.0 — расхождение | Severity: HIGH
AP-F04 | docs/MANUAL_TESTS.md | Нет тест-сценариев для /expenses, /report, /areas, inline callbacks (v5.7.0–v5.9.0) | Severity: HIGH
AP-F04 | docs/USER_GUIDE_admin.md | Описан старый Admin интерфейс (v1.0). Новые: ReplyKeyboard 12 команд, inline панель 6 секций, action callbacks (v5.7.0) | Severity: HIGH
AP-F04 | docs/USER_GUIDE_owner.md | Отсутствуют /expenses, /report handlers (добавлены v5.7.x) | Severity: HIGH
AP-F04 | docs/USER_GUIDE_staff.md | Аналогично USER_GUIDE_owner.md | Severity: HIGH
AP-F04 | docs/DEPLOY.md | Описывает Oracle Cloud ARM Ubuntu — проект переехал на GCP europe-west3-b 2026-03-03 | Severity: HIGH
AP-F02 | docs/IMPROVEMENT_MASTER_PLAN.md | Заголовок «Status: ACTIVE», но v2 явно указывает что v1 закрыт в v5.7.0 | Severity: MEDIUM
AP-F04 | docs/COMMAND_AUDIT.md | Аудит остановлен на Batch 5 — /expenses, /report, /areas из Batch 6 не аудированы | Severity: MEDIUM
AP-F04 | docs/COMMAND_AUDIT_ADMIN.md | Останов на v5.3.0 — inline action callbacks (📝/🏷️/👤/⏰) v5.9.0 не задокументированы | Severity: MEDIUM
AP-F01 | docs/plans/2026-03-02-merge-vtb-cf-plan.md | Не обновлялся 10 дней, через 4 дня перейдёт в stale (14-дневный порог) | Severity: LOW
AP-F01 | docs/plans/2026-03-02-unified-telegram-bot.md | Аналогично — через 4 дня stale | Severity: LOW
AP-F03 | docs/AUDIT_2026-03-03.md | Заголовок указывает «АКТУАЛЕН», но прошло 9 дней — нарушение протокола (>7 дней = УСТАРЕЛ) | Severity: LOW
```

---

## PHASE 3: CONTENT DRIFT TABLE

| Файл | Упомянутая версия | Текущая версия | Что изменилось | Severity |
|------|-------------------|----------------|----------------|----------|
| docs/ARCHITECTURE.md | v4.0 (Phase 0 + Batch 1-4) | v5.9.0 | +i18n модуль, +/expenses, +/report, 5→3 ботов, 11→13 handlers | HIGH |
| docs/MANUAL_TESTS.md | v4.3.0+ | v5.9.0 | Новые команды /expenses, /report, /areas, /events, inline кнопки | HIGH |
| docs/USER_GUIDE_admin.md | v1.0 | v5.9.0 | Admin ReplyKeyboard + inline панель (apanel:) + action callbacks | HIGH |
| docs/USER_GUIDE_owner.md | 2026-03-03 | v5.9.0 | /expenses, /report handlers | HIGH |
| docs/USER_GUIDE_staff.md | 2026-03-03 | v5.9.0 | /expenses, /report handlers | HIGH |
| docs/DEPLOY.md | Oracle Cloud | GCP | Весь деплой-процесс изменён | HIGH |
| docs/IMPROVEMENT_MASTER_PLAN.md | ACTIVE | CLOSED (v5.7.0) | Статус файла неверный | MEDIUM |
| docs/COMMAND_AUDIT.md | Batch 5 | Batch 6 | /expenses, /report, /areas, /events не проверены | MEDIUM |
| docs/COMMAND_AUDIT_ADMIN.md | v5.3.0 | v5.9.0 | Inline action callbacks не задокументированы | MEDIUM |

---

## PHASE 4: SYNTHESIS

### Итоговые метрики

| Метрика | Значение | Target | Статус |
|---------|---------|--------|--------|
| Всего файлов .md | 40 | — | — |
| Файлов с content-stale | 9 (live docs) | 0 | 🔴 CRITICAL |
| AP-F04 нарушений (code-doc drift) | 8 | 0 | 🔴 CRITICAL |
| AP-F02 нарушений (version drift) | 3 | 0 | 🔴 CRITICAL |
| AP-F01 нарушений (time-stale) | 2 | 0 | 🟡 WARNING |
| AP-F03 нарушений (stale status) | 1 | 0 | 🟡 WARNING |
| Untracked файлов | 1 | 0 | 🟡 WARNING |

### Приоритизированный план исправлений

#### Критичные (исправить немедленно):

1. **docs/ARCHITECTURE.md** — обновить до v5.9.0: 3 бота, 14 подсистем, 47 таблиц, Batch 5-6
2. **docs/USER_GUIDE_admin.md** — добавить Admin ReplyKeyboard, inline панель, action callbacks
3. **docs/MANUAL_TESTS.md** — добавить сценарии /expenses, /report, /areas, inline callbacks
4. **docs/DEPLOY.md** — пометить как Oracle Cloud УСТАРЕЛО или переместить в archive/

#### Высокие (следующая сессия):

5. **docs/USER_GUIDE_owner.md**, **docs/USER_GUIDE_staff.md** — добавить /expenses, /report
6. **docs/COMMAND_AUDIT_ADMIN.md** — обновить до v5.9.0 с action callbacks
7. **docs/COMMAND_AUDIT.md** — добавить Batch 6 команды

#### Средние:

8. **docs/IMPROVEMENT_MASTER_PLAN.md** — изменить статус на CLOSED, обновить ссылку в CLAUDE.md на v2
9. **docs/plans/2026-03-02-*.md** — переместить в docs/archive/plans/ до порога stale
10. **docs/AUDIT_2026-03-03.md** — обновить статус заголовка на УСТАРЕЛ

---

## VERIFICATION SCORE: 2/5

| Критерий | Статус | Причина |
|---------|--------|---------|
| Свежесть (date-based) | PASS | Все файлы обновлены < 14 дней |
| Актуальность контента | FAIL | 9 live docs содержат content drift |
| Нет code-doc drift | FAIL | docs/ARCHITECTURE.md v4.0 при v5.9.0 |
| AP-F0X нарушений нет | FAIL | 14 нарушений AP-F01..AP-F04 |
| Нет stale статусов | FAIL | AUDIT_2026-03-03 «АКТУАЛЕН» через 9 дней |

**Итог: 2/5 — документация свежа по дате, но критически устарела по содержимому**

---

*Отчёт сгенерирован: 2026-03-12 | docs-optimizer skill v1.0 | freshness mode | AP-F0X коды применены*
