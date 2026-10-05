# Integration Guardian

Каждая интеграция должна быть надёжной и безопасной.

## Что это

Супер-скилл, объединяющий 4 специализированных скилла в единый guardian workflow:

- **security-audit** — OWASP Top 10, CVE check, hardcoded secrets
- **webhook-processor** — HMAC + async + idempotency + retry + DLQ
- **dependency-updater** — аудит pip зависимостей по severity
- **cicd-pipeline** — GitHub Actions: lint → test → security → build → deploy

## Быстрый старт

| Задача | Режим |
|--------|-------|
| Новый платформенный бот (WA/FB/IG/Viber) | `hardening` |
| Добавить webhook endpoint | `webhook` |
| Security review перед деплоем | `audit` |
| Обновить requirements.txt | `deps` |
| Настроить CI/CD pipeline | `ci` |

## Файлы

```
SKILL.md                                 — полная документация (5 режимов, synergy rules)
references/
  hmac-patterns.md                       — HMAC для Meta/Viber/Telegram/GitHub/Stripe
  cicd-security.md                       — GitHub Actions security gates (pip-audit, bandit, trivy)
assets/
  templates/
    webhook-handler.py                   — production-ready FastAPI webhook шаблон
    github-actions-ci.yml                — полный CI/CD workflow для GCP deploy
  checklists/
    pre-deploy-security.md               — чеклист перед каждым деплоем (8 блоков)
```

## Главное правило

Новый платформенный коннектор в Omni Inbox не считается готовым, пока не прошёл `hardening` mode Guardian.
