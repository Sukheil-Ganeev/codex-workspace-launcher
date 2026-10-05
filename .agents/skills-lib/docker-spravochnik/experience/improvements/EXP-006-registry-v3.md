---
id: EXP-006
date: 2026-02-17
type: improvement
severity: medium
tags: [registry, migration, breaking-changes]
---

## Паттерн

Docker Registry v3 -- GA с июня 2025, не RC как утверждал критик.

## Когда использовать

При развёртывании self-hosted registry или миграции с v2 на v3.

## Решение

Registry v3 (rebranded как "distribution"):
- **GA** с июня 2025 (CNCF graduated project)
- Путь конфига изменён: `/etc/distribution/config.yml` (был `/etc/docker/registry/config.yml`)
- Удалены storage drivers: OSS, Swift
- Новые фичи: улучшенный garbage collection, поддержка OCI artifacts

При миграции v2 -> v3:
1. Проверить storage driver (если OSS/Swift -- мигрировать на S3/filesystem)
2. Обновить путь конфига
3. Протестировать GC

```bash
docker run -d -p 5000:5000 --name registry registry:3
```

## Урок

При описании новых версий -- указывать breaking changes при миграции, а не только "стабильная". Пользователям важно знать что сломается.
