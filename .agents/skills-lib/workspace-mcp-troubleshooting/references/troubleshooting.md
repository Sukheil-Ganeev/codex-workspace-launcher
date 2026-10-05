# Детальный Troubleshooting

## Проблема 1: Токены не работают после авторизации (ГЛАВНАЯ)

### Симптомы
- Авторизация завершается успешно
- В браузере показывается "Authentication successful"
- Файл токена создаётся в `~/.google_workspace_mcp/credentials/`
- Но при запросе снова требует авторизацию

### Корневая причина
workspace-mcp в stdio режиме хранит токены **только в памяти**. Файлы credentials создаются для персистентности, но **НЕ загружаются** при старте сервера.

Это баг/особенность библиотеки — в исходном коде `get_credentials()` пытается читать файлы, но в stdio режиме с uvx это не работает корректно.

### Пошаговое решение

```bash
# 1. Убить зависший OAuth сервер
bash ~/.claude/scripts/kill-oauth-server.sh

# 2. Очистить кэш uvx (опционально, если есть ошибки)
rm -rf ~/AppData/Local/uv/cache/builds-v0/
```

```
# 3. Переподключить MCP
/mcp
```

```
# 4. Авторизоваться — пройти по ссылке, завершить flow
# 5. Сделать запрос с ТЕМ ЖЕ email что авторизовали
# 6. После успеха — другие аккаунты тоже заработают
```

---

## Проблема 2: Invalid or expired OAuth state parameter

### Симптомы
После авторизации в Google появляется:
```
Authentication Processing Error
Invalid or expired OAuth state parameter
```

### Причина
OAuth state хранится в памяти Python процесса MCP сервера. Если старый MinimalOAuthServer остался висеть на порту 8000:
1. Новый MCP сервер генерирует state в СВОЮ память
2. Google делает callback на localhost:8000
3. Callback приходит на СТАРЫЙ процесс
4. Старый процесс не знает о новом state → ошибка

### Диагностика
```bash
netstat -ano | grep ":8000"
```
Если видите процесс — это потенциально старый OAuth сервер.

### Решение
```bash
bash ~/.claude/scripts/kill-oauth-server.sh
/mcp
# Авторизоваться заново
```

---

## Проблема 3: uvx ошибка шифрования (os error 6000)

### Симптомы
```
error: failed to copy file... Указанный файл не может быть зашифрован. (os error 6000)
```

### Причина
Windows блокирует файлы в кэше uvx из-за настроек шифрования или антивируса.

### Решение
```bash
rm -rf ~/AppData/Local/uv/cache/builds-v0/
/mcp
```

---

## Проблема 4: Токены разных аккаунтов

### Симптомы
Есть несколько Google аккаунтов, хочу использовать конкретный.

### Решение
1. Авторизуй нужный аккаунт
2. Используй его email в параметре `user_google_email`
3. Файлы токенов хранятся отдельно для каждого email:
   ```
   ~/.google_workspace_mcp/credentials/
   ├── account1@gmail.com.json
   ├── account2@gmail.com.json
   └── account3@gmail.com.json
   ```

### Важно
После перезапуска Claude Code нужно снова "активировать" хотя бы один аккаунт через авторизацию.

---

## Проблема 5: MCP сервер не запускается

### Симптомы
- `/mcp` выдаёт ошибку
- Инструменты Google Workspace недоступны

### Диагностика
```bash
uvx --version
pip show workspace-mcp
cat ~/.claude/settings.json | grep -A15 "google_workspace"
```

### Решение
1. Проверить что uvx установлен
2. Проверить конфигурацию в settings.json
3. Убедиться что есть OAuth credentials (CLIENT_ID и CLIENT_SECRET)

---

## Проблема 6: Access denied / Insufficient permissions

### Симптомы
Ошибка при доступе к Google Drive/Gmail/etc

### Причина
Недостаточно scopes при авторизации

### Решение
1. Удалить старые токены:
```bash
rm ~/.google_workspace_mcp/credentials/проблемный@gmail.com.json
```
2. Авторизоваться заново, согласиться на ВСЕ разрешения
