---
id: EXP-005
date: 2026-02-17
type: improvement
severity: medium
tags: [mcp, toolkit, catalog, ai]
---

## Паттерн

Docker MCP Toolkit -- управление MCP-серверами из Docker Desktop.

## Когда использовать

Когда нужно подключить MCP-серверы к Claude, Cursor или другим AI-инструментам. Docker обеспечивает изоляцию, безопасность и простоту установки MCP-серверов.

## Решение

- **MCP Catalog** на Docker Hub: готовые MCP-серверы (postgres, github, filesystem и др.)
- **MCP Gateway:** Docker Desktop выступает прокси между AI-клиентами и MCP-серверами
- Все образы `mcp/` подписаны и проверены
- Поддержка: Claude Desktop, VS Code (Copilot), Cursor, Windsurf

Установка: Docker Desktop -> Settings -> MCP Toolkit -> Enable

## Урок

MCP-экосистема в Docker -- новая, но важная для AI-разработчиков. Упрощает установку MCP-серверов с одного клика вместо ручной настройки через npx/uvx.
