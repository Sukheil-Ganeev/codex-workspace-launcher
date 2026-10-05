---
name: codex-session-maintenance
description: Использовать для регулярного обслуживания Codex Session Vault: обновить аудит, README, dashboard, PLAN, список хвостов, проверить приватность экспортов и выбрать следующий пакет сессий.
---

# Codex Session Maintenance

## Назначение

Поддерживать Vault актуальным, чтобы история Codex-сессий не превращалась в хаос.

## Рабочий порядок

1. Обновить аудит:

```powershell
python .\tools\codex_session_vault.py --codex-home C:\Users\londo\.codex --out .\docs\codex-session-vault
```

2. Проверить свежие числа в:

- `README.md`;
- `dashboard.html`;
- `PLAN.md`;
- `remaining-session-work-YYYY-MM-DD.md`.

3. Проверить приватность:

```powershell
git status --ignored --short -- docs/codex-session-vault
git check-ignore -v docs/codex-session-vault/exports/<slug>/session.jsonl
```

4. Выбрать следующий пакет 10-20 сессий.
5. Обновить `exports/batch-export-plan-YYYY-MM-DD.md`.
6. Не коммитить приватные стенограммы, индексы и сырые кандидаты.

## Когда остановиться

Остановиться и объяснить риск, если:

- выбранный пакет включает сессии 250 МБ+ без отдельного тяжелого режима;
- в git видны `session.jsonl`, `session.md`, `session.html`;
- пользователь просит удалить или перенести оригинальные сессии без явного подтверждения;
- рабочее дерево грязное и задача требует массового `git add -A`.

