# ops-sentinel

Супер-скилл: каждый деплой виден, каждый сбой алертится, каждый инцидент решён по runbook.

Объединяет `monitoring-observability`, `integration-guardian` и `docker-справочник` в единый ops workflow для VIP-DXB-CatalogBot (7 ботов на GCP VM tourist-bot).

## Быстрый старт

```
ops-sentinel: setup / target: "Max Bot (порт 8085)"
ops-sentinel: deploy-verify / after: "Phase 22 push to main"
ops-sentinel: alert-design / bot: "Instagram"
ops-sentinel: incident / type: "webhook-dead" / platform: "facebook"
ops-sentinel: full / new-bot: "Max Bot" / port: 8085
```

## Файлы

| Файл | Назначение |
|------|-----------|
| `SKILL.md` | Полное описание 5 режимов, synergy rules, platform map |
| `references/runbook-advanced.md` | 5 runbooks (RB-01..RB-05) + escalation matrix |
| `references/metrics-catalog.md` | Что измерять, пороги, как собирать |
| `assets/templates/health-endpoint.py` | FastAPI /health endpoint с DB check |
| `assets/templates/alert-rules.py` | core/alerts.py с cooldown и pre-built helpers |
| `assets/templates/structlog-setup.py` | JSON logging + PII sanitizer + correlation ID |
| `assets/checklists/post-deploy-verify.md` | 7-layer smoke test после git push |

## Связанные скиллы

- `monitoring-observability` — детальный structlog, Grafana, Prometheus
- `integration-guardian` — HMAC audit, webhook security, CVE scan, CI pipeline
- `docker-справочник` — Docker production patterns
