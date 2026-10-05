# Hotfix Workflow - Экстренное исправление в production

## Введение

**Ситуация:** В production обнаружен критический баг. Пользователи не могут войти в систему из-за ошибки в функции аутентификации.

**Требование:** Исправить немедленно, минуя обычный процесс code review.

**Время:** Максимум 30 минут от обнаружения до deploy.

---

## Шаг 1: Проверка текущего состояния

Перед началом hotfix убедись в чистоте рабочей директории.

```bash
# Проверка состояния
git status

# Если есть незакоммиченные изменения - сохрани их
git stash save "WIP: текущая работа перед hotfix"
```

**Пример вывода:**
```
On branch develop
Your branch is up to date with 'origin/develop'.

nothing to commit, working tree clean
```

---

## Шаг 2: Переключение на production ветку (main/master)

Hotfix всегда создается от последней версии production.

```bash
# Переключись на main
git checkout main

# Получи последние изменения с сервера
git pull origin main
```

**Пример вывода:**
```
Switched to branch 'main'
Your branch is up to date with 'origin/main'.
Already up to date.
```

---

## Шаг 3: Создание hotfix ветки

Hotfix ветки имеют специальное именование: `hotfix/описание-проблемы`

```bash
# Создай hotfix ветку от main
git checkout -b hotfix/fix-login-authentication
```

**Пример вывода:**
```
Switched to a new branch 'hotfix/fix-login-authentication'
```

**Важно:**
- Hotfix ветка всегда от `main` (production)
- Название должно четко описывать проблему
- Используй префикс `hotfix/`

---

## Шаг 4: Исправление бага

Открой файл с проблемой и исправь баг.

**Файл:** `src/auth/login.js`

**До исправления:**
```javascript
function validatePassword(password) {
  // БАГ: Проверка возвращает undefined вместо boolean
  if (password.length >= 8) {
    return true;
  }
}
```

**После исправления:**
```javascript
function validatePassword(password) {
  // ИСПРАВЛЕНО: Явно возвращаем false для коротких паролей
  if (password.length >= 8) {
    return true;
  }
  return false;  // Добавлена эта строка
}
```

---

## Шаг 5: Быстрое тестирование

Hotfix требует минимального, но обязательного тестирования.

```bash
# Запусти тесты для модуля аутентификации
npm test -- auth

# Проверь вручную основной сценарий
npm start
# Попробуй войти с коротким паролем (должна быть ошибка)
# Попробуй войти с правильным паролем (должен быть вход)
```

**Важно:** Тестируй только критический функционал, не задерживай deploy.

---

## Шаг 6: Коммит исправления

Коммит в hotfix должен быть максимально информативным.

```bash
# Добавь изменения
git add src/auth/login.js

# Коммит с подробным описанием
git commit -m "hotfix: исправлена валидация пароля при входе

Проблема:
- Функция validatePassword возвращала undefined для коротких паролей
- Это приводило к пропуску валидации и ошибкам входа

Решение:
- Добавлен явный return false для паролей короче 8 символов
- Теперь функция всегда возвращает boolean

Протестировано:
- Вход с коротким паролем (3 символа) - отклонен
- Вход с правильным паролем (10 символов) - успешен

Priority: CRITICAL
Ticket: PROD-1234"
```

**Пример вывода:**
```
[hotfix/fix-login-authentication a1b2c3d] hotfix: исправлена валидация пароля при входе
 1 file changed, 1 insertion(+)
```

---

## Шаг 7: Push hotfix ветки

```bash
# Отправь hotfix ветку на GitHub
git push origin hotfix/fix-login-authentication
```

**Пример вывода:**
```
Enumerating objects: 7, done.
Counting objects: 100% (7/7), done.
Delta compression using up to 8 threads
Compressing objects: 100% (4/4), done.
Writing objects: 100% (4/4), 642 bytes | 642.00 KiB/s, done.
Total 4 (delta 3), reused 0 (delta 0)
To github.com:username/project.git
 * [new branch]      hotfix/fix-login-authentication -> hotfix/fix-login-authentication
```

---

## Шаг 8: Быстрый merge в main (production)

Для hotfix можно делать прямой merge без Pull Request (если процесс позволяет).

```bash
# Переключись на main
git checkout main

# Влей hotfix
git merge --no-ff hotfix/fix-login-authentication

# Создай tag для версии
git tag -a v1.2.1 -m "Hotfix: исправлена валидация пароля"

# Отправь main и tag на сервер
git push origin main
git push origin v1.2.1
```

**Пример вывода:**
```
Switched to branch 'main'
Merge made by the 'recursive' strategy.
 src/auth/login.js | 1 +
 1 file changed, 1 insertion(+)
```

**Важно:** Флаг `--no-ff` создает merge commit, сохраняя историю hotfix.

---

## Шаг 9: Merge в develop (чтобы не потерять исправление)

Критически важно: hotfix должен попасть и в develop ветку!

```bash
# Переключись на develop
git checkout develop

# Получи последние изменения
git pull origin develop

# Влей hotfix
git merge --no-ff hotfix/fix-login-authentication

# Отправь develop на сервер
git push origin develop
```

**Пример вывода:**
```
Switched to branch 'develop'
Merge made by the 'recursive' strategy.
 src/auth/login.js | 1 +
 1 file changed, 1 insertion(+)
```

---

## Шаг 10: Удаление hotfix ветки

После успешного merge удали hotfix ветку.

```bash
# Удали локальную ветку
git branch -d hotfix/fix-login-authentication

# Удали удаленную ветку
git push origin --delete hotfix/fix-login-authentication
```

**Пример вывода:**
```
Deleted branch hotfix/fix-login-authentication (was a1b2c3d).
To github.com:username/project.git
 - [deleted]         hotfix/fix-login-authentication
```

---

## Шаг 11: Deploy в production

```bash
# SSH на production сервер
ssh user@production-server

# Перейди в директорию проекта
cd /var/www/project

# Получи последние изменения (включая hotfix)
git pull origin main

# Перезапусти сервис
sudo systemctl restart app-service

# Проверь логи
sudo journalctl -u app-service -n 50
```

---

## Шаг 12: Проверка в production

```bash
# Проверь статус сервиса
curl https://yourapp.com/health

# Попробуй войти через API
curl -X POST https://yourapp.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123"}'

# Должна быть ошибка валидации, а не системная ошибка
```

**Ожидаемый ответ:**
```json
{
  "error": "Password must be at least 8 characters",
  "code": "VALIDATION_ERROR"
}
```

---

## Шаг 13: Уведомление команды

Отправь уведомление в Slack / Email о hotfix.

**Шаблон сообщения:**
```
🔥 HOTFIX DEPLOYED

Проблема: Пользователи не могли войти из-за ошибки валидации паролей
Решение: Исправлена логика в validatePassword()
Версия: v1.2.1
Время downtime: ~5 минут
Статус: Исправлено и проверено

Ветки обновлены:
✅ main (production)
✅ develop

Deploy: 15:45 UTC
Проверено: Вход работает корректно
```

---

## Шаг 14: Вернись к своей работе

Если до hotfix у тебя была незавершенная работа - восстанови ее.

```bash
# Вернись на свою рабочую ветку
git checkout feature/your-current-work

# Восстанови stash (если делал)
git stash pop
```

---

## Полная последовательность команд (чек-лист)

```bash
# 1. Подготовка
git status
git stash save "WIP before hotfix"

# 2. Создание hotfix
git checkout main
git pull origin main
git checkout -b hotfix/fix-issue-name

# 3. Исправление и коммит
# ... редактируй файлы ...
git add .
git commit -m "hotfix: описание проблемы и решения"

# 4. Тестирование
npm test
# ... проверь вручную ...

# 5. Merge в main
git checkout main
git merge --no-ff hotfix/fix-issue-name
git tag -a v1.2.1 -m "Hotfix description"
git push origin main
git push origin v1.2.1

# 6. Merge в develop
git checkout develop
git pull origin develop
git merge --no-ff hotfix/fix-issue-name
git push origin develop

# 7. Cleanup
git branch -d hotfix/fix-issue-name
git push origin --delete hotfix/fix-issue-name

# 8. Возврат к работе
git checkout your-feature-branch
git stash pop
```

---

## Когда использовать hotfix workflow

**Используй hotfix когда:**
- Баг в production блокирует работу пользователей
- Безопасность под угрозой
- Финансовые потери
- Нарушение SLA (Service Level Agreement)

**НЕ используй hotfix когда:**
- Баг не критичный (можно подождать релиза)
- Это новая фича (даже если "очень нужна")
- Требуется большое изменение кода
- Баг только в develop/staging

---

## Типичные ошибки при hotfix

### Ошибка 1: Забыл влить hotfix в develop
```bash
# НЕПРАВИЛЬНО: hotfix только в main
git checkout main
git merge hotfix/fix
git push

# ПРАВИЛЬНО: hotfix и в main, и в develop
git checkout main
git merge hotfix/fix
git push

git checkout develop
git merge hotfix/fix
git push
```

### Ошибка 2: Создал hotfix от develop
```bash
# НЕПРАВИЛЬНО: hotfix от develop
git checkout develop
git checkout -b hotfix/fix

# ПРАВИЛЬНО: hotfix от main
git checkout main
git checkout -b hotfix/fix
```

### Ошибка 3: Забыл создать tag
```bash
# НЕПРАВИЛЬНО: merge без tag
git merge hotfix/fix

# ПРАВИЛЬНО: merge с tag
git merge hotfix/fix
git tag -a v1.2.1 -m "Hotfix description"
git push origin v1.2.1
```

---

## GitHub Desktop альтернатива

Если используешь GitHub Desktop вместо командной строки:

1. **Current branch** → выбери `main`
2. **Fetch origin** (получи последние изменения)
3. **Current branch** → **New branch** → `hotfix/fix-issue-name`
4. Исправь код в редакторе
5. В GitHub Desktop:
   - Отметь измененные файлы
   - Напиши commit message
   - Нажми **Commit to hotfix/fix-issue-name**
6. **Publish branch** (отправь на GitHub)
7. **Current branch** → выбери `main`
8. **Branch** → **Merge into current branch** → выбери `hotfix/fix-issue-name`
9. **Push origin**
10. **Current branch** → выбери `develop`
11. **Branch** → **Merge into current branch** → выбери `hotfix/fix-issue-name`
12. **Push origin**

---

## Timing для hotfix процесса

| Этап | Время | Примечание |
|------|-------|------------|
| Диагностика бага | 5-10 мин | Понять причину |
| Создание hotfix ветки | 1 мин | git checkout -b |
| Исправление кода | 5-15 мин | Минимальное изменение |
| Тестирование | 3-5 мин | Только критичное |
| Коммит и push | 2 мин | git commit + push |
| Merge в main | 2 мин | git merge + tag |
| Merge в develop | 2 мин | git merge |
| Deploy | 3-5 мин | Зависит от инфраструктуры |
| Проверка | 2-3 мин | Smoke test |
| **ИТОГО** | **25-45 мин** | От бага до fix |

---

## Заключение

Hotfix workflow - это экстренный процесс для критических багов. Главные принципы:

1. Всегда от `main` (production)
2. Минимальное изменение кода
3. Быстрое тестирование
4. Merge и в `main`, и в `develop`
5. Обязательный tag версии
6. Немедленный deploy
7. Уведомление команды

**Помни:** Hotfix - это исключение, не правило. Для обычных багов используй стандартный feature branch workflow.
