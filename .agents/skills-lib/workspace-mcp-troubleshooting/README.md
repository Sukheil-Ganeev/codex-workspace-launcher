# workspace-mcp-troubleshooting

Скилл для диагностики и решения проблем с Google Workspace MCP сервером.

## Структура

```
workspace-mcp-troubleshooting/
├── SKILL.md              # Основной файл с решениями
├── README.md             # Этот файл
└── references/
    ├── troubleshooting.md    # Детальный troubleshooting
    └── cheatsheet.md         # Быстрые команды
```

## Когда использовать

- "Invalid or expired OAuth state parameter"
- Проблемы с авторизацией Google
- Порт 8000 занят
- MCP сервер не отвечает

## Быстрый старт

При ошибке OAuth state:
```bash
bash ~/.claude/scripts/kill-oauth-server.sh
```
Затем `/mcp`
