---
id: EXP-004
date: 2026-02-16
type: warning
severity: high
tags: [computer-tool, mcp-schema, action-set]
source: experience/_index.md
---

## Риск

Смешение generic Anthropic `computer_use` (15 actions) с реальной схемой Claude in Chrome MCP приводит к несуществующим вызовам.

## Факт

В Claude in Chrome `computer` поддерживает 13 actions:
`left_click`, `right_click`, `double_click`, `triple_click`, `type`, `screenshot`, `wait`, `scroll`, `key`, `left_click_drag`, `zoom`, `scroll_to`, `hover`.

## Урок

Опирайся на фактическую MCP-схему, а не на общий API-контекст из других инструментов.