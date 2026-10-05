---
name: workspace-mcp-troubleshooting
description: "Диагностика и решение проблем Google Workspace MCP сервера. OAuth ошибки, порты, авторизация."
---
# Workspace MCP Troubleshooting

Скилл для диагностики и решения проблем с Google Workspace MCP сервером.

## ГЛАВНАЯ ПРОБЛЕМА: Токены не читаются после авторизации

### Симптомы
- Авторизация проходит успешно ("Authentication successful")
- Токен сохраняется в `~/.google_workspace_mcp/credentials/email.json`
- Но при следующем запросе снова требует авторизацию

### Причина
workspace-mcp в stdio режиме **не читает токены из файлов автоматически**. Токены хранятся в памяти процесса. После перезапуска MCP сервера память очищается.

### Решение (проверено 04.02.2026)

**Шаг 1:** Убить зависшие процессы на порту 8000
```bash
bash ~/.claude/scripts/kill-oauth-server.sh
```

**Шаг 2:** Переподключить MCP
```
/mcp
```

**Шаг 3:** Авторизоваться с ЛЮБЫМ аккаунтом
- Пройти по ссылке авторизации
- Завершить OAuth flow
- Дождаться "Authentication successful"

**Шаг 4:** Сделать запрос с ТЕМ ЖЕ аккаунтом
```
list_drive_items(user_google_email="авторизованный@gmail.com")
```

**Шаг 5:** Теперь можно использовать ДРУГИЕ аккаунты
После первой успешной авторизации, токены других аккаунтов (если они есть в файлах) тоже начинают работать.

### Почему так происходит
1. uvx запускает workspace-mcp в изолированном окружении
2. При старте сервер НЕ загружает токены из файлов
3. После успешной авторизации токен попадает В ПАМЯТЬ сервера
4. Сервер начинает работать с этим токеном
5. Побочный эффект: другие токены из файлов тоже "активируются"

---

## Проблема: "Invalid or expired OAuth state parameter"

### Причина
Старый callback-сервер висит на порту 8000. OAuth state хранится в памяти текущего MCP процесса, а callback приходит на старый процесс.

### Решение
```bash
# Убить процесс на порту 8000
bash ~/.claude/scripts/kill-oauth-server.sh

# Или вручную
netstat -ano | grep ":8000" | grep "LISTENING" | awk '{print $5}' | xargs -I{} taskkill //PID {} //F
```

Затем переподключить MCP: `/mcp`

---

## Проблема: Порт 8000 занят

### Диагностика
```bash
netstat -ano | grep ":8000"
```

### Решение
```bash
PID=$(netstat -ano | grep ":8000" | grep "LISTENING" | head -1 | awk '{print $5}')
taskkill //PID $PID //F
```

---

## Проблема: uvx выдаёт ошибку шифрования

### Симптомы
```
error: failed to copy file... Указанный файл не может быть зашифрован. (os error 6000)
```

### Решение
Очистить кэш uv:
```bash
rm -rf ~/AppData/Local/uv/cache/builds-v0/
```
Затем `/mcp`

---

## Архитектура

```
┌─────────────────────────────────────────────────────────┐
│  Claude Code                                            │
│  ├── MCP Server (uvx workspace-mcp)                     │
│  │   ├── OAuth21SessionStore (_global_store) [В ПАМЯТИ] │
│  │   │   ├── _oauth_states: {state: {session_id, ttl}}  │
│  │   │   └── _sessions: {email: credentials}            │
│  │   └── MinimalOAuthServer (thread on :8000)           │
│  │       └── /oauth2callback → validate_state()         │
│  └── Credentials files [НА ДИСКЕ, но не читаются!]      │
│      └── ~/.google_workspace_mcp/credentials/*.json     │
└─────────────────────────────────────────────────────────┘

ВАЖНО: Файлы credentials сохраняются на диск, но НЕ загружаются
автоматически при старте сервера в stdio режиме!
```

## Конфигурация

**Расположение:** `~/.claude/settings.json`

```json
{
  "mcpServers": {
    "google_workspace": {
      "command": "uvx",
      "args": ["workspace-mcp"],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "xxx.apps.googleusercontent.com",
        "GOOGLE_OAUTH_CLIENT_SECRET": "GOCSPX-xxx",
        "OAUTHLIB_INSECURE_TRANSPORT": "1"
      }
    }
  }
}
```

## OAuth Flow

1. `start_google_auth` → генерирует state, сохраняет в `_oauth_states` (память)
2. Пользователь переходит по URL, авторизуется в Google
3. Google редиректит на `localhost:8000/oauth2callback?code=xxx&state=yyy`
4. `MinimalOAuthServer` получает callback
5. `handle_auth_callback` → `validate_and_consume_oauth_state(state)`
6. Если state найден и валиден → обмен code на tokens
7. Tokens сохраняются:
   - В память (`_sessions`) — используется для запросов
   - В файл (`~/.google_workspace_mcp/credentials/`) — для персистентности (но не читается при старте!)

**TTL для state:** 600 секунд (10 минут)

## Полезные команды

| Команда | Описание |
|---------|----------|
| `/mcp` | Переподключить MCP серверы |
| `bash ~/.claude/scripts/kill-oauth-server.sh` | Убить OAuth сервер |
| `netstat -ano \| grep 8000` | Проверить порт 8000 |
| `ls ~/.google_workspace_mcp/credentials/` | Сохранённые токены |
| `rm -rf ~/AppData/Local/uv/cache/builds-v0/` | Очистить кэш uvx |

## Скрипт kill-oauth-server.sh

**Расположение:** `~/.claude/scripts/kill-oauth-server.sh`

```bash
#!/bin/bash
PID=$(netstat -ano 2>/dev/null | grep ":8000" | grep "LISTENING" | head -1 | awk '{print $5}')
if [ -n "$PID" ] && [ "$PID" != "0" ]; then
    taskkill //PID $PID //F 2>/dev/null || kill -9 $PID 2>/dev/null
    echo "Killed process $PID on port 8000"
else
    echo "Port 8000 is already free"
fi
```

## История решения проблемы (04.02.2026)

### Что пробовали и не сработало:
1. Добавление `MCP_SINGLE_USER_MODE=1` в env — не помогло
2. Добавление `WORKSPACE_MCP_CREDENTIALS_DIR` — не помогло
3. Смена `uvx` на `python -m workspace_mcp` — не помогло
4. Запуск в режиме `streamable-http` через URL — не помогло
5. Обновление версии workspace-mcp — заблокировано Windows

### Что сработало:
1. Убить процесс на порту 8000
2. Очистить кэш uvx
3. `/mcp` для переподключения
4. Авторизоваться с одним аккаунтом (ganeevsukheil@gmail.com)
5. Сделать успешный запрос с этим аккаунтом
6. После этого другие аккаунты (lutikbravlstarsd@gmail.com) тоже заработали

### Вывод:
Баг в workspace-mcp — токены не загружаются из файлов при старте в stdio режиме. Нужна "прогревочная" авторизация после каждого перезапуска Claude Code.

## Ссылки

- GitHub: https://github.com/taylorwilsdon/google_workspace_mcp
- PyPI: https://pypi.org/project/workspace-mcp/
- Issues: https://github.com/taylorwilsdon/google_workspace_mcp/issues
