# delivery-docs

После шипа — вся документация обновлена автоматически.

## Quick Start

```
delivery-docs full: Phase 22 Max Bot завершена
delivery-docs release: обнови changelog для v10.9.0
delivery-docs api-spec: задокументируй max_bot/app.py
delivery-docs docstrings: get_or_create_max_user()
delivery-docs visual-delta: что изменилось после Phase 22
```

## Файлы

| Файл | Назначение |
|------|-----------|
| `SKILL.md` | Главный файл: все 5 режимов, примеры, правила |
| `references/changelog-advanced.md` | Keep a Changelog, SemVer, Conventional Commits |
| `references/openapi-patterns.md` | FastAPI OpenAPI patterns, drift detection |
| `assets/templates/release-notes-ru.md` | Шаблон release notes на русском |
| `assets/templates/openapi-base.yaml` | Базовый OpenAPI 3.x template |

## Режимы

| Режим | Что делает |
|-------|-----------|
| `release` | CHANGELOG.md + CLAUDE.md таблица + user summary на русском |
| `api-spec` | OpenAPI YAML из FastAPI кода + drift detection |
| `docstrings` | Google-style docstrings для Python функций |
| `visual-delta` | Mermaid архитектурная диаграмма до/после |
| `full` | Все четыре режима за один прогон |
