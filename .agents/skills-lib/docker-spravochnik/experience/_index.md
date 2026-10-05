# Docker-справочник: Опыт и уроки

> Читать при активации скилла!
> Дата: 2026-02-17

## Статистика

| Категория | Записей |
|-----------|---------|
| Fixes | 3 |
| Improvements | 3 |
| Patterns | 2 |
| Warnings | 2 |
| **Всего** | **10** |

## Критические уроки (топ-5)

### EXP-001: Docker Hub Rate Limits [critical]
Unauthenticated = 10 pulls/час (с 1 апреля 2025). Personal = 100/час. Pro/Team/Business = безлимитно.
→ Всегда `docker login` в CI. `--pull=missing` вместо `--pull=always`.

### EXP-009: Watchtower ARCHIVED [critical]
Заархивирован декабрь 2025. Несовместим Docker 28+. Альтернативы: WUD, DIUN.

### EXP-002: Цены Docker Desktop [critical]
Актуальные (декабрь 2024+): Pro=$9, Team=$15, Business=$24. Старые цены $7/$11/$21 -- устаревшие.

### EXP-003: pip --no-deps ломает контейнер [high]
НЕ использовать `pip install --no-deps` без lock-файла. Правильно: `--no-cache-dir`.

### EXP-010: Deprecated -- всегда 3 параметра [high]
Для deprecated указывать: 1) дата прекращения, 2) несовместимая версия, 3) конкретные альтернативы.

## Индекс по категориям

### Fixes
| ID | Тема | Severity | Файл |
|----|------|----------|------|
| EXP-001 | Rate Limits противоречия | critical | fixes/EXP-001-rate-limits.md |
| EXP-002 | Docker pricing ошибка | critical | fixes/EXP-002-docker-pricing.md |
| EXP-003 | pip --no-deps | high | fixes/EXP-003-pip-no-deps.md |

### Improvements
| ID | Тема | Severity | Файл |
|----|------|----------|------|
| EXP-004 | Docker Model Runner | medium | improvements/EXP-004-model-runner.md |
| EXP-005 | Docker MCP Toolkit | medium | improvements/EXP-005-mcp-toolkit.md |
| EXP-006 | Registry v3 GA | medium | improvements/EXP-006-registry-v3.md |

### Patterns
| ID | Тема | Severity | Файл |
|----|------|----------|------|
| EXP-007 | compose.yaml имя | medium | patterns/EXP-007-compose-yaml-name.md |
| EXP-008 | Docker vs Podman | low | patterns/EXP-008-docker-vs-podman.md |

### Warnings
| ID | Тема | Severity | Файл |
|----|------|----------|------|
| EXP-009 | Watchtower archived | critical | warnings/EXP-009-watchtower-archived.md |
| EXP-010 | Deprecated 3 параметра | high | warnings/EXP-010-deprecated-3-params.md |

## Дополнительные уроки (компактные)

- golang base image: `golang:1.26-bookworm` (не alpine), alpine ломает CGO
- BuildKit: дефолт с Engine 23.0 (январь 2023), не с 25.0
- Ubuntu 20.04 ESM: НЕ использовать для новых Docker-хостов
- DCT удалён из CLI в Engine 29, собирается как плагин
- Docker Desktop 4.60: текущая стабильная (февраль 2026)
- Compose v5.x: ренумерация с v2.32.0 → v5.0.0 (ноябрь 2024)
