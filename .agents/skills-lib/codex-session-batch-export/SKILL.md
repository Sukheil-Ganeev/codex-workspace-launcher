---
name: codex-session-batch-export
description: Использовать, когда нужно пакетно экспортировать выбранные Codex-сессии из sessions-index.csv в приватный Vault через копии JSONL и codlogs, с лимитом размера, манифестом и защитой от случайного экспорта гигантских сессий.
---

# Codex Session Batch Export

## Назначение

Пакетно экспортировать выбранные Codex-сессии в `docs/codex-session-vault/exports`, не трогая оригинальную папку `C:\Users\londo\.codex\sessions`.

## Правила

- Сначала должен быть свежий `sessions-index.csv`.
- Сначала должен быть план `exports/batch-export-plan-YYYY-MM-DD.md`.
- Полные `session.jsonl`, `session.md`, `session.html` считать приватными.
- Не использовать `--include-tool-results` по умолчанию.
- Сессии 250 МБ+ экспортировать только по одной и только после проверки размера/места.
- Не коммитить приватные export-папки.

## Команда

Из проекта:

```powershell
python .\tools\codex_session_batch_export.py --index .\docs\codex-session-vault\sessions-index.csv --out .\docs\codex-session-vault\exports --session <thread-id>=<slug>
```

Из глобального навыка:

```powershell
python C:\Users\londo\.codex\skills\codex-session-vault\scripts\codex_session_batch_export.py --index <sessions-index.csv> --out <exports-folder> --session <thread-id>=<slug>
```

## Проверка

После экспорта проверить:

```powershell
git status --ignored --short -- docs/codex-session-vault/exports
```

Ожидаемо: приватные папки экспорта должны быть `!!`, а безопасные отчеты и манифест могут быть `M` или `??`.

