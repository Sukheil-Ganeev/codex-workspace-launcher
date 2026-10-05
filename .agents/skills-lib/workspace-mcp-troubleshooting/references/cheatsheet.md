# Workspace MCP Cheatsheet

## После перезапуска Claude Code (ВАЖНО!)

```bash
# 1. Убить зависший OAuth сервер
bash ~/.claude/scripts/kill-oauth-server.sh

# 2. Переподключить MCP
/mcp

# 3. Авторизоваться с любым аккаунтом (пройти по ссылке)
# 4. Сделать запрос с этим же аккаунтом
# 5. Теперь все аккаунты работают!
```

## Быстрые команды

### OAuth ошибки
```bash
# Убить зависший OAuth сервер
bash ~/.claude/scripts/kill-oauth-server.sh

# Проверить порт 8000
netstat -ano | grep ":8000"

# Вручную убить процесс на порту
netstat -ano | grep ":8000" | grep "LISTENING" | awk '{print $5}' | xargs -I{} taskkill //PID {} //F
```

### Кэш uvx (если ошибки шифрования)
```bash
rm -rf ~/AppData/Local/uv/cache/builds-v0/
```

### MCP команды
```
/mcp              # Переподключить все MCP серверы
```

### Проверка токенов
```bash
# Где хранятся credentials
ls ~/.google_workspace_mcp/credentials/

# Удалить токен конкретного аккаунта (для ре-авторизации)
rm ~/.google_workspace_mcp/credentials/email@gmail.com.json
```

### Версия пакета
```bash
pip show workspace-mcp
uvx workspace-mcp --version
```

## Частые ошибки

| Ошибка | Решение |
|--------|---------|
| Invalid or expired OAuth state | `kill-oauth-server.sh` + `/mcp` |
| Требует авторизацию снова и снова | Авторизоваться → сделать запрос с тем же email |
| Port 8000 already in use | Убить процесс на порту |
| os error 6000 (шифрование) | Очистить кэш uvx |
| No credentials found | Авторизоваться заново |

## Алгоритм "Прогрева" MCP после рестарта

```
1. /mcp
2. Вызвать любой Google инструмент → получить ссылку авторизации
3. Пройти авторизацию в браузере
4. Вызвать инструмент с ТЕМ ЖЕ email → успех!
5. Теперь другие email тоже работают
```

## Файлы

| Путь | Описание |
|------|----------|
| `~/.claude/settings.json` | Конфигурация MCP серверов |
| `~/.claude/scripts/kill-oauth-server.sh` | Скрипт очистки порта 8000 |
| `~/.google_workspace_mcp/credentials/` | Токены Google аккаунтов |
| `~/AppData/Local/uv/cache/` | Кэш uvx |
