# Fork Workflow - Вклад в чужой open-source проект

## Введение

**Ситуация:** Ты нашел баг в open-source проекте на GitHub. У тебя НЕТ прямого доступа к репозиторию, но хочешь внести исправление.

**Решение:** Fork workflow - создай копию (fork) репозитория, исправь баг там, затем предложи изменения через Pull Request.

---

## Шаг 1: Fork репозитория на GitHub

1. Открой репозиторий проекта: `github.com/author/original-project`
2. Нажми кнопку **Fork** (правый верхний угол)
3. Выбери свой аккаунт
4. Жди завершения (5-10 секунд)

**Результат:** Создан `yourusername/original-project` в твоем аккаунте.

---

## Шаг 2: Clone своего fork локально

```bash
# Клонируй СВОЙ fork (не оригинал!)
git clone https://github.com/yourusername/original-project.git
cd original-project
```

---

## Шаг 3: Добавление upstream (оригинальный репозиторий)

```bash
# Добавь оригинальный репозиторий как upstream
git remote add upstream https://github.com/author/original-project.git

# Проверка
git remote -v
```

**Вывод:**
```
origin    https://github.com/yourusername/original-project.git (fetch)
origin    https://github.com/yourusername/original-project.git (push)
upstream  https://github.com/author/original-project.git (fetch)
upstream  https://github.com/author/original-project.git (push)
```

**Объяснение:**
- `origin` - твой fork (для push)
- `upstream` - оригинальный проект (для обновлений)

---

## Шаг 4: Синхронизация с upstream

```bash
# Получи изменения из upstream
git fetch upstream

# Переключись на main
git checkout main

# Влей изменения из upstream
git merge upstream/main

# Отправь в свой fork
git push origin main
```

---

## Шаг 5: Создание feature ветки

```bash
# Создай ветку от актуального main
git checkout -b fix-null-pointer-bug
```

**Именование:**
- `fix/bug-description` - багфиксы
- `feature/new-feature` - новые фичи
- `docs/update-readme` - документация

---

## Шаг 6: Внесение изменений

**Пример:** Исправление null pointer в `src/utils/validator.js`

**До:**
```javascript
function validateEmail(email) {
  return email.includes('@');  // Ошибка если email = null
}
```

**После:**
```javascript
function validateEmail(email) {
  if (!email) return false;  // Защита от null/undefined
  return email.includes('@');
}
```

---

## Шаг 7: Добавление тестов

```javascript
// tests/validator.test.js
test('validateEmail handles null input', () => {
  expect(validateEmail(null)).toBe(false);
  expect(validateEmail(undefined)).toBe(false);
});
```

```bash
npm test  # Проверь что тесты проходят
```

---

## Шаг 8: Коммит изменений

```bash
git add src/utils/validator.js tests/validator.test.js

git commit -m "fix: handle null/undefined in validateEmail

- Added null/undefined check before includes()
- Prevents TypeError when email is null
- Added test cases

Fixes #1234"
```

**Важно:** `Fixes #1234` автоматически закроет issue #1234 при merge.

---

## Шаг 9: Push в свой fork

```bash
git push origin fix-null-pointer-bug
```

---

## Шаг 10: Создание Pull Request

1. Открой свой fork на GitHub
2. Увидишь: **Compare & pull request** для ветки `fix-null-pointer-bug`
3. Нажми **Compare & pull request**

**Title:**
```
fix: handle null/undefined in validateEmail
```

**Description:**
```markdown
## Problem
validateEmail() throws TypeError with null input

## Solution
Added null check before includes()

## Testing
- Added unit tests
- All tests passing

Fixes #1234
```

4. Нажми **Create pull request**

---

## Шаг 11: Code Review процесс

Maintainers проверят PR и могут попросить изменения.

**Внесение правок:**

```bash
# Внеси изменения локально
code src/utils/validator.js

# Коммит в ту же ветку
git add .
git commit -m "docs: update JSDoc"

# Push (автоматически добавится в PR)
git push origin fix-null-pointer-bug
```

---

## Шаг 12: После merge - cleanup

```bash
# Переключись на main
git checkout main

# Получи обновления (включая твой merge)
git fetch upstream
git merge upstream/main

# Обнови свой fork
git push origin main

# Удали feature ветку
git branch -d fix-null-pointer-bug
git push origin --delete fix-null-pointer-bug
```

---

## Регулярная синхронизация fork

Перед началом новой работы:

```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

**Или через GitHub UI:**
1. Открой свой fork
2. "This branch is 15 commits behind author:main"
3. **Sync fork** → **Update branch**

---

## Работа с несколькими PR

```bash
# PR 1: Баг
git checkout main
git pull upstream main
git checkout -b fix-memory-leak
# ... изменения ...
git push origin fix-memory-leak
# Создай PR #1

# PR 2: Фича (пока PR #1 в review)
git checkout main  # От актуального main!
git pull upstream main
git checkout -b feature-add-timeout
# ... изменения ...
git push origin feature-add-timeout
# Создай PR #2
```

**Важно:** Всегда от актуального `main`, не от других feature веток!

---

## Обновление PR после изменений в upstream

```bash
# Твоя feature ветка
git checkout fix-null-pointer-bug

# Получи обновления
git fetch upstream

# Rebase на актуальный main
git rebase upstream/main

# Разреши конфликты если есть
# git add <файлы>
# git rebase --continue

# Force push (PR обновится)
git push origin fix-null-pointer-bug --force-with-lease
```

---

## Типичные ошибки

### Ошибка 1: Работа в main

```bash
# НЕПРАВИЛЬНО
git checkout main
# ... изменения в main ...
```

**Правильно:** Всегда feature ветка!

### Ошибка 2: Нет upstream

```bash
# НЕПРАВИЛЬНО: только origin
git remote -v
```

**Правильно:** Добавь upstream!

### Ошибка 3: Push в upstream

```bash
# НЕПРАВИЛЬНО
git push upstream fix-bug
# ERROR: Permission denied
```

**Правильно:** Push только в `origin`.

---

## Checklist для Fork Workflow

```
[ ] Fork на GitHub (UI)
[ ] Clone своего fork
[ ] Добавить upstream
[ ] Синхронизация с upstream
[ ] Создать feature ветку
[ ] Внести изменения
[ ] Добавить тесты
[ ] Коммит
[ ] Push в свой fork
[ ] Создать PR
[ ] Code review правки
[ ] После merge: cleanup
```

---

## Полная последовательность команд

```bash
# 1. Fork на GitHub (UI)

# 2. Clone и настройка
git clone https://github.com/yourusername/project.git
cd project
git remote add upstream https://github.com/author/project.git

# 3. Синхронизация
git fetch upstream
git checkout main
git merge upstream/main
git push origin main

# 4. Feature ветка
git checkout -b fix-bug

# 5. Изменения и коммит
# ... редактируй файлы ...
git add .
git commit -m "fix: description"

# 6. Push и PR
git push origin fix-bug
# Создай PR через GitHub UI

# 7. После merge
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
git branch -d fix-bug
```

---

## GitHub CLI (gh) альтернатива

```bash
# Fork и clone
gh repo fork author/project --clone

# Создание PR
git checkout -b fix-bug
# ... изменения ...
gh pr create --title "fix: bug" --body "Details"

# Проверка PR
gh pr status

# Синхронизация
gh repo sync
```

---

## Заключение

Fork workflow для open-source вкладов:

1. **Fork** - создай копию проекта
2. **Clone** - скачай свой fork
3. **Upstream** - добавь оригинальный репозиторий
4. **Feature branch** - работай в отдельных ветках
5. **Tests** - добавляй тесты
6. **PR** - создавай понятный Pull Request
7. **Review** - реагируй на feedback
8. **Cleanup** - удаляй ветки после merge
9. **Sync** - регулярно синхронизируй с upstream

**Первый вклад:** Найди проект с меткой "good first issue" и сделай PR!
