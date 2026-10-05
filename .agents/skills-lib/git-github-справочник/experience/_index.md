# Git/GitHub - Critical Lessons Learned

**Последнее обновление:** 2026-02-05

## Топ-5 Критических уроков

### 1. НИКОГДА не push --force на shared branches
**Проблема:** Перезаписывает историю других разработчиков
**Решение:** Используй --force-with-lease или избегай force push
```bash
# ОПАСНО
git push --force origin main

# БЕЗОПАСНЕЕ (проверяет что remote не изменился)
git push --force-with-lease origin feature-branch

# ЛУЧШЕ - избегай rewrite на shared branches
git revert <commit>  # вместо reset
```

### 2. Secrets в git history = security breach
**Проблема:** Даже удалённые файлы остаются в истории
**Решение:** .gitignore + git-filter-repo для очистки
```bash
# Предотвращение
echo ".env" >> .gitignore
echo "*.key" >> .gitignore

# Очистка истории (если уже закоммитил)
git filter-repo --path .env --invert-paths
```

### 3. Conventional commits для чистой истории
**Проблема:** "fix", "update", "changes" - бесполезные сообщения
**Решение:** Формат type(scope): description
```bash
# Хорошие примеры
git commit -m "feat(auth): add JWT token refresh"
git commit -m "fix(api): handle null response from payment gateway"
git commit -m "docs(readme): update installation instructions"
git commit -m "refactor(booking): extract validation logic"

# Типы: feat, fix, docs, style, refactor, test, chore
```

### 4. Feature branches + Pull Requests
**Проблема:** Работа напрямую в main = конфликты и баги
**Решение:** Branch per feature + code review
```bash
# Workflow
git checkout -b feature/payment-integration
# ... работа ...
git push -u origin feature/payment-integration
# Создать PR через GitHub
# После merge:
git checkout main
git pull
git branch -d feature/payment-integration
```

### 5. git stash для быстрого переключения контекста
**Проблема:** Uncommitted changes блокируют checkout
**Решение:** Stash сохраняет изменения временно
```bash
# Сохранить текущую работу
git stash push -m "WIP: payment form"

# Переключиться на другую задачу
git checkout hotfix/urgent-bug

# Вернуться и восстановить
git checkout feature/payment
git stash pop
```

## Дополнительные уроки

### Git aliases для продуктивности
```bash
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --all"
```

### Resolve merge conflicts
```bash
# Посмотреть конфликтные файлы
git status

# После ручного разрешения
git add <resolved-file>
git commit -m "merge: resolve conflicts in payment.js"
```

### Undo последний commit (не pushed)
```bash
git reset --soft HEAD~1  # сохранить изменения
git reset --hard HEAD~1  # удалить изменения
```

---

**Файлов в experience/:** 1
**Будет пополняться:** Да, при использовании справочника
