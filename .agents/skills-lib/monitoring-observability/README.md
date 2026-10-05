# monitoring-observability

Production monitoring и observability для Python ботов (VIP-DXB-CatalogBot).

## Файлы

- `SKILL.md` — основной скилл: 5 режимов (setup, health, dashboard, alerts, runbook)
- `references/runbook-templates.md` — готовые runbook для 5 типов инцидентов

## Режимы

| Режим | Когда использовать |
|-------|--------------------|
| `setup` | Настроить structured logging для нового бота |
| `health` | Добавить `/health` endpoint к webhook-серверу |
| `dashboard` | Настроить Grafana + Prometheus метрики |
| `alerts` | Добавить Telegram-алерты при превышении порогов |
| `runbook` | Дебаг production-инцидента по шаблону |

## Runbook-ы

- RB-01: Telegram/VK бот не отвечает
- RB-02: Webhook перестал получать события
- RB-03: DB Pool Exhausted
- RB-04: AI Search Quota Exceeded
- RB-05: GCP VM недоступна
