# Domain Plugin Packs Roadmap

Дата: 2026-05-22

## Зачем

Если навыков сотни, пользователю нужна не простыня названий, а понятные рабочие наборы.

## Рекомендуемые packs

| Pack | Для чего | Примеры навыков |
|---|---|---|
| `design-ui-pack` | сайты, панели, UX, визуальная QA | frontend-design, design-an-interface, figma, frontend-testing-debugging |
| `docs-ops-pack` | README, статусы, changelog, runbook | doc-ops, docs-optimizer, delivery-docs, update-docs |
| `content-growth-pack` | X, SMM, контент, воронки | x-viral-business-strategist, content-engine, copywriting, ad-creative |
| `security-qa-pack` | audit, tests, threat model, path safety | codex-security, e2e-testing, code-review, diagnose |
| `agent-automation-pack` | meta-skills, orchestration, MCP, browser-use | skill-orchestrator-master, agent-factory, browser-use-ops, plugin-creator |
| `business-strategy-pack` | офферы, исследования, GTM, PM | competitive-analysis, pm-strategy, customer-research, business-health-diagnostic |

## Правило сборки

1. В pack добавлять только навыки с понятным `description`.
2. Источник и дата импорта фиксируются в `references/source-map.md`.
3. Pack проходит validation до установки.
4. Runtime mirrors обновляются только копированием из canonical pack.
