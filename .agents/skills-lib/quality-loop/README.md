# quality-loop

Супер-скилл: написать фичу правильно с первого раза.
Объединяет `tdd`, `feature-blueprint` и `code-refactor-pro` в единый workflow.

## Quick Start

```
quality-loop: plan-test / task: "Реализовать get_or_create_max_user() для Max Bot"
quality-loop: cycle / function: "MaxConnector.handle_message()"
quality-loop: snapshot / module: "bot/handlers/catalog.py"
quality-loop: cleanup / scope: "bot/handlers/omni.py"
quality-loop: verify / feature: "Max Bot Phase 22"
```

## Режимы

| Режим | Когда |
|-------|-------|
| `plan-test` | Перед написанием нового кода |
| `cycle` | RED → GREEN → REFACTOR для одной функции |
| `snapshot` | Перед рефакторингом существующего кода |
| `cleanup` | После кодинга, перед PR |
| `verify` | Финальная проверка перед деплоем |

## Навигация

- `SKILL.md` — полная документация всех режимов, синергий, примеров
- `references/test-strategy.md` — тестирование 7 платформ, async паттерны
- `references/refactor-safety.md` — characterization tests, feature flags, rollback
- `assets/templates/test-stub-async.py` — шаблон pytest stub файла
- `assets/templates/refactor-checklist.md` — чеклист before/after рефакторинга
- `assets/checklists/done-definition.md` — Definition of Done
