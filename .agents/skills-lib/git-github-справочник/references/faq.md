# FAQ - Часто задаваемые вопросы по Git и GitHub

Ответы на популярные вопросы о работе с Git и GitHub.

---

## Основы Git и GitHub

### ❓ Чем Git отличается от GitHub?

**Git** - это система контроля версий (программа на вашем компьютере):
- Работает локально на вашем ПК
- Отслеживает историю изменений
- Позволяет работать с ветками, откатывать изменения
- Можно использовать без интернета

**GitHub** - это облачный сервис для хостинга Git репозиториев:
- Хранит ваши репозитории в облаке
- Позволяет работать в команде
- Предоставляет UI для просмотра кода, Pull Requests, Issues
- Есть аналоги: GitLab, Bitbucket

**Аналогия:** Git - это Word на вашем компьютере, GitHub - это Google Docs для совместной работы.

---

### ❓ Что такое коммит (commit)?

**Коммит** - это снимок (snapshot) состояния проекта в определённый момент времени.

```bash
# Каждый коммит содержит:
- Изменения в файлах (diff)
- Автора и дату
- Сообщение описывающее что изменилось
- Уникальный ID (hash)
```

**Аналогия:** Как сохранение игры в определённой точке - можно вернуться к этому моменту.

**Пример:**
```bash
git add file.txt
git commit -m "Add user login functionality"
# Создан коммит с hash: a1b2c3d
```

---

### ❓ Что такое ветка (branch)?

**Ветка** - это независимая линия разработки.

```bash
main ──●──●──●──●
           \
    feature \──●──●
```

**Зачем нужны ветки:**
- Работать над новой функцией не трогая основной код
- Несколько человек могут работать параллельно
- Экспериментировать без риска сломать проект
- Легко откатить неудачные изменения

**Типичный workflow:**
```bash
git checkout -b feature-login    # Создать ветку для новой функции
# Работаем, коммитим...
git checkout main                # Вернуться на main
git merge feature-login          # Слить изменения
```

---

### ❓ В чём разница между git pull и git fetch?

| Команда | Что делает | Изменяет локальные файлы |
|---------|-----------|-------------------------|
| `git fetch` | Скачивает изменения с сервера, **НЕ** применяет их | ❌ Нет |
| `git pull` | Скачивает изменения **И** сливает с текущей веткой | ✅ Да |

**`git fetch`** - безопасный способ посмотреть что изменилось:
```bash
git fetch origin
git log HEAD..origin/main  # Посмотреть что нового
git merge origin/main      # Слить если нужно
```

**`git pull`** = `git fetch` + `git merge`:
```bash
git pull origin main
# Эквивалентно:
git fetch origin
git merge origin/main
```

💡 **Рекомендация:** Используйте `fetch` когда хотите сначала посмотреть изменения, `pull` когда уверены что хотите слить.

---

### ❓ Когда использовать merge, а когда rebase?

**Merge** - создаёт merge commit, сохраняет всю историю:
```bash
main    ●──●──●────●  (merge commit)
             \    /
   feature    ●──●
```
```bash
git checkout main
git merge feature
```

**Rebase** - переписывает историю, перемещает коммиты:
```bash
main    ●──●──●──●──●  (feature коммиты перенесены)
```
```bash
git checkout feature
git rebase main
```

**Когда использовать:**

| Ситуация | Команда | Почему |
|----------|---------|--------|
| Публичная ветка (main) | `merge` | Сохраняет историю, безопасно |
| Личная feature ветка | `rebase` | Чистая история, линейный граф |
| Перед Pull Request | `rebase` | Актуализировать с main |
| Уже push'нутые коммиты | `merge` | Rebase перепишет историю |

⚠️ **Золотое правило:** Никогда не делайте rebase публичных веток!

---

### ❓ Что такое HEAD в Git?

**HEAD** - это указатель на текущий коммит (обычно на последний коммит текущей ветки).

```bash
main    ●──●──●──●  ← HEAD (вы здесь)
```

**Обозначения:**
- `HEAD` - текущий коммит
- `HEAD~1` или `HEAD~` - предыдущий коммит (родитель)
- `HEAD~2` - два коммита назад
- `HEAD^` - первый родитель (для merge коммитов)

**Примеры:**
```bash
git show HEAD         # Показать текущий коммит
git reset HEAD~1      # Откатить последний коммит
git diff HEAD~3       # Сравнить с 3 коммита назад
```

**Detached HEAD** - когда переключились на конкретный коммит (не на ветку):
```bash
git checkout abc123   # Теперь HEAD указывает на abc123, не на ветку
```

---

### ❓ Что такое .gitignore и как им пользоваться?

**`.gitignore`** - файл со списком файлов/папок которые Git должен игнорировать.

**Зачем:**
- Исключить временные файлы
- Не коммитить зависимости (node_modules)
- Не загружать секреты (.env, credentials)

**Пример .gitignore:**
```
# Зависимости
node_modules/
venv/

# Секреты
.env
.env.local
secrets.txt

# Временные файлы
*.log
*.tmp
.cache/

# OS файлы
.DS_Store
Thumbs.db

# IDE настройки
.vscode/
.idea/
```

**Как использовать:**
```bash
# 1. Создать .gitignore в корне проекта
echo "node_modules/" > .gitignore

# 2. Закоммитить
git add .gitignore
git commit -m "Add .gitignore"

# Теперь node_modules/ будет игнорироваться
```

💡 **Совет:** Используйте https://gitignore.io для генерации .gitignore под ваш стек.

---

## Работа с изменениями

### ❓ Как отменить последний коммит?

**Зависит от того, что вы хотите сделать:**

**1. Отменить коммит, оставить изменения для редактирования:**
```bash
git reset --soft HEAD~1
# Изменения остаются в staging area
```

**2. Отменить коммит, вернуть изменения в unstaged:**
```bash
git reset HEAD~1
# Изменения в рабочей директории, не в staging
```

**3. Полностью удалить коммит и изменения:**
```bash
git reset --hard HEAD~1
# ⚠️ Опасно! Изменения потеряны
```

**4. Создать новый коммит отменяющий предыдущий (для публичных веток):**
```bash
git revert HEAD
# Безопасно, не меняет историю
```

**Если коммит уже push'нут:**
```bash
# Вариант 1: Revert (рекомендуется)
git revert HEAD
git push

# Вариант 2: Force push (опасно!)
git reset --hard HEAD~1
git push --force-with-lease
```

---

### ❓ Как изменить commit message?

**Если коммит не push'нут:**
```bash
git commit --amend -m "New correct message"
```

**Если коммит уже push'нут:**
```bash
git commit --amend -m "New correct message"
git push --force-with-lease origin feature-branch
```

⚠️ **Внимание:** Force push опасен для shared веток (main/develop)!

**Изменить несколько старых коммитов:**
```bash
git rebase -i HEAD~3
# В редакторе замените pick на reword для нужных коммитов
```

---

### ❓ Как удалить файл из Git, но оставить его локально?

```bash
# Удалить из tracking, оставить на диске
git rm --cached file.txt

# Удалить папку
git rm --cached -r node_modules/

# Добавить в .gitignore чтобы не добавился снова
echo "file.txt" >> .gitignore

# Закоммитить
git add .gitignore
git commit -m "Remove file.txt from tracking"
```

---

### ❓ Как посмотреть что изменилось в коммите?

```bash
# Последний коммит
git show

# Конкретный коммит
git show abc123

# Только имена файлов
git show --name-only abc123

# Статистика изменений
git show --stat abc123

# Конкретный файл в коммите
git show abc123:path/to/file.txt
```

---

### ❓ Как найти когда и кем была изменена конкретная строка кода?

```bash
# Показать автора каждой строки
git blame file.txt

# Показать строки 10-20
git blame -L 10,20 file.txt

# С email
git blame -e file.txt

# Игнорировать whitespace изменения
git blame -w file.txt
```

**Для визуального просмотра:**
- В VS Code: GitLens расширение
- На GitHub: нажать "Blame" при просмотре файла

---

### ❓ Как временно сохранить изменения не коммитя?

**Используйте `git stash`:**

```bash
# Сохранить текущие изменения
git stash

# Переключиться на другую ветку, поработать...
git checkout hotfix-branch

# Вернуться и восстановить изменения
git checkout feature-branch
git stash pop
```

**Продвинутое использование:**
```bash
# Сохранить с описанием
git stash save "WIP: implementing login"

# Список всех stash
git stash list

# Применить конкретный stash
git stash apply stash@{1}

# Посмотреть что в stash
git stash show -p

# Удалить stash
git stash drop stash@{0}

# Создать ветку из stash
git stash branch new-feature-branch
```

---

## Работа с ветками

### ❓ Как создать новую ветку?

```bash
# Создать ветку (не переключаясь)
git branch feature-login

# Создать и переключиться
git checkout -b feature-login

# Современный способ (Git 2.23+)
git switch -c feature-login

# Создать ветку на основе другой
git checkout -b hotfix origin/main
```

---

### ❓ Как удалить ветку?

```bash
# Удалить локальную ветку (безопасно)
git branch -d feature-login

# Принудительно удалить
git branch -D feature-login

# Удалить удалённую ветку
git push origin --delete feature-login

# Альтернативный синтаксис
git push origin :feature-login
```

**Удалить все локальные ветки которые слиты:**
```bash
git branch --merged main | grep -v "main" | xargs git branch -d
```

---

### ❓ Как переименовать ветку?

```bash
# Переименовать текущую ветку
git branch -m new-name

# Переименовать другую ветку
git branch -m old-name new-name

# Если ветка уже push'нута:
git branch -m old-name new-name
git push origin --delete old-name
git push -u origin new-name
```

---

### ❓ Как синхронизировать форк с оригинальным репозиторием?

```bash
# 1. Добавить upstream (один раз)
git remote add upstream https://github.com/original/repo.git

# 2. Синхронизация (регулярно)
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

**Альтернатива - через GitHub UI:**
1. Открыть ваш форк на GitHub
2. Нажать "Sync fork"
3. Нажать "Update branch"

---

### ❓ Как применить коммит из другой ветки в текущую?

**Используйте `cherry-pick`:**

```bash
# Применить один коммит
git cherry-pick abc123

# Применить несколько коммитов
git cherry-pick abc123 def456

# Применить диапазон коммитов
git cherry-pick abc123..def456

# Применить без создания коммита (для редактирования)
git cherry-pick -n abc123
```

**Пример использования:**
```bash
# В feature ветке сделали важный bugfix
# Хотим применить его в main без всей feature

git checkout main
git cherry-pick <bugfix-commit-hash>
git push origin main
```

---

## Работа с remote репозиториями

### ❓ Как изменить URL remote репозитория?

```bash
# Посмотреть текущий URL
git remote -v

# Изменить URL
git remote set-url origin https://github.com/user/new-repo.git

# Изменить с HTTPS на SSH
git remote set-url origin git@github.com:user/repo.git
```

---

### ❓ Как подключить локальный репозиторий к GitHub?

```bash
# 1. Создайте пустой репозиторий на GitHub (без README)

# 2. В локальной директории:
git init
git add .
git commit -m "Initial commit"

# 3. Подключить remote
git remote add origin https://github.com/user/repo.git

# 4. Push'нуть
git push -u origin main
```

---

### ❓ Как склонировать только одну ветку?

```bash
# Клонировать только main ветку
git clone --single-branch --branch main https://github.com/user/repo.git

# Shallow clone (без истории)
git clone --depth 1 https://github.com/user/repo.git

# Комбинация (одна ветка + последний коммит)
git clone --single-branch --branch main --depth 1 https://github.com/user/repo.git
```

---

### ❓ Как загрузить большой файл в Git?

**Git не предназначен для больших файлов (видео, архивы, бинарники > 100MB).**

**Решения:**

**1. Git LFS (Large File Storage):**
```bash
# Установить Git LFS
git lfs install

# Отслеживать большие файлы
git lfs track "*.psd"
git lfs track "*.mp4"

# Добавить .gitattributes
git add .gitattributes

# Обычный workflow
git add video.mp4
git commit -m "Add video"
git push
```

**2. Хранить файлы отдельно:**
- Использовать CDN
- Облачное хранилище (Dropbox, Google Drive)
- В README ссылка на скачивание

**3. Добавить в .gitignore:**
```bash
echo "large-files/" >> .gitignore
```

---

## GitHub специфика

### ❓ Что такое Pull Request (PR)?

**Pull Request** - запрос на слияние вашей ветки в другую ветку.

**Зачем нужен:**
- Code review - другие проверяют ваш код
- Обсуждение изменений
- Автоматические тесты (CI/CD)
- История изменений

**Workflow:**
```bash
# 1. Создать feature ветку
git checkout -b feature-login

# 2. Работать и коммитить
git add .
git commit -m "Add login"

# 3. Push'нуть ветку
git push -u origin feature-login

# 4. На GitHub создать Pull Request
# feature-login → main

# 5. После review и одобрения - слить PR
# 6. Удалить ветку
git checkout main
git pull
git branch -d feature-login
```

---

### ❓ Чем отличается Fork от Clone?

**Clone** - копия репозитория на ваш компьютер:
```bash
git clone https://github.com/user/repo.git
# Теперь есть локальная копия
```

**Fork** - копия репозитория на вашем GitHub аккаунте:
- Нажать "Fork" на GitHub
- Создаётся `your-user/repo` на вашем аккаунте
- Можно вносить изменения
- Можно отправить Pull Request в оригинальный репозиторий

**Типичный workflow для contribution:**
```bash
# 1. Fork на GitHub
# 2. Clone вашего форка
git clone https://github.com/YOUR-USER/repo.git

# 3. Добавить upstream
git remote add upstream https://github.com/ORIGINAL-USER/repo.git

# 4. Работать и push'ить в ваш форк
git push origin feature

# 5. Создать Pull Request на GitHub
# YOUR-USER/repo:feature → ORIGINAL-USER/repo:main
```

---

### ❓ Как создать Pull Request через командную строку?

**Используйте GitHub CLI (`gh`):**

```bash
# Установить gh: https://cli.github.com

# Создать PR
gh pr create --title "Add login feature" --body "Description"

# Интерактивное создание
gh pr create

# Создать draft PR
gh pr create --draft

# Посмотреть список PR
gh pr list

# Просмотр PR
gh pr view 123

# Checkout чужого PR
gh pr checkout 123

# Слить PR
gh pr merge 123
```

---

### ❓ Что такое GitHub Actions?

**GitHub Actions** - встроенная CI/CD система в GitHub.

**Для чего:**
- Автоматически запускать тесты
- Деплоить приложение
- Проверять код линтером
- Создавать релизы

**Пример - автотесты при PR:**
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm install
      - run: npm test
```

✅ **Подробнее:** См. `github-workflows.md` для готовых примеров.

---

## Продвинутые вопросы

### ❓ Как восстановить удалённый файл/коммит?

**Файл удалён но не закоммичен:**
```bash
git restore file.txt
```

**Файл удалён и закоммичен:**
```bash
# 1. Найти когда удалён
git log --all --full-history -- path/to/file.txt

# 2. Восстановить из коммита перед удалением
git checkout <commit-hash>^ -- path/to/file.txt

# 3. Закоммитить
git commit -m "Restore file.txt"
```

**Коммит удалён (git reset --hard):**
```bash
# 1. Найти в reflog
git reflog

# 2. Восстановить
git checkout <commit-hash>
git checkout -b recovery-branch
```

---

### ❓ Как очистить историю от чувствительных данных?

**⚠️ Если случайно закоммитили пароли/ключи:**

**1. Сначала смените пароль/ключ!** (данные уже в истории)

**2. Удалить из истории:**
```bash
# Установить git-filter-repo
pip install git-filter-repo

# Удалить файл из всей истории
git filter-repo --invert-paths --path secrets.txt

# Добавить в .gitignore
echo "secrets.txt" >> .gitignore

# Force push
git push --force --all origin
```

**Альтернатива через BFG:**
```bash
# Скачать bfg.jar
java -jar bfg.jar --delete-files secrets.txt repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

---

### ❓ Как работать с несколькими GitHub аккаунтами?

**Используйте SSH ключи для разных аккаунтов:**

```bash
# 1. Создать разные SSH ключи
ssh-keygen -t ed25519 -C "work@example.com" -f ~/.ssh/id_work
ssh-keygen -t ed25519 -C "personal@example.com" -f ~/.ssh/id_personal

# 2. Добавить в ssh-agent
ssh-add ~/.ssh/id_work
ssh-add ~/.ssh/id_personal

# 3. Создать ~/.ssh/config
Host github-work
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_work

Host github-personal
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_personal

# 4. Использовать в remote URL
git remote add origin git@github-work:company/repo.git
git remote add origin git@github-personal:user/repo.git
```

---

### ❓ Как перенести коммиты из одной ветки в другую?

```bash
# Применить последние 3 коммита из feature в main
git checkout main
git cherry-pick feature~3..feature

# Перенести всю ветку на другую базу
git rebase --onto new-base old-base feature
```

---

### ❓ Как разделить большой коммит на несколько маленьких?

```bash
# 1. Откатить последний коммит, оставив изменения
git reset HEAD~1

# 2. Добавлять файлы частями
git add file1.js
git commit -m "Add feature part 1"

git add file2.js
git commit -m "Add feature part 2"

# Или использовать git add -p для интерактивного выбора
git add -p
```

---

### ❓ Как объединить несколько коммитов в один?

**Используйте interactive rebase:**

```bash
# Объединить последние 3 коммита
git rebase -i HEAD~3

# В редакторе:
# pick abc123 First commit
# squash def456 Second commit   ← изменить на squash
# squash ghi789 Third commit    ← изменить на squash

# Сохранить, отредактировать commit message
```

---

### ❓ Как создать пустой коммит?

**Зачем:** Триггер CI/CD, закрытие issue, тестирование.

```bash
git commit --allow-empty -m "Trigger CI build"
git push
```

---

## Best Practices

### ❓ Как писать хорошие commit messages?

**Структура:**
```
Краткий заголовок (до 50 символов)

Подробное описание если нужно (с новой строки после пустой):
- Что изменилось
- Почему изменилось
- Какие есть побочные эффекты

Fixes #123
```

**Правила:**
- ✅ Используйте повелительное наклонение: "Add feature" (не "Added" или "Adding")
- ✅ Начинайте с заглавной буквы
- ✅ Не ставьте точку в конце заголовка
- ✅ Объясняйте "почему", а не "что" (что видно в diff)
- ✅ Ссылайтесь на issues: "Fixes #123"

**Примеры:**

❌ Плохо:
```
fix bug
updated files
changes
```

✅ Хорошо:
```
Fix login redirect for authenticated users

Previously authenticated users were redirected to /home
instead of /dashboard after login. This updates the redirect
logic to check user role.

Fixes #456
```

---

### ❓ Как часто нужно коммитить?

**Правило:** Коммитьте логически завершённые изменения.

✅ **Хорошая практика:**
- После завершения функции
- После исправления бага
- Перед переключением на другую задачу
- В конце рабочего дня (как минимум)

❌ **Плохая практика:**
- Один гигантский коммит в конце недели
- Коммит после каждой изменённой строки
- "WIP" коммиты в main ветке

💡 **Совет:** Коммитьте часто в feature ветке, используйте `git rebase -i` перед merge для очистки истории.

---

### ❓ Стоит ли коммитить node_modules или venv?

❌ **Нет!** Зависимости не должны быть в Git.

**Почему:**
- Огромный размер репозитория
- Проблемы с разными OS
- Merge conflicts
- Долгий clone

**Правильный подход:**
```bash
# 1. Добавить в .gitignore
echo "node_modules/" >> .gitignore
echo "venv/" >> .gitignore

# 2. Коммитить package.json / requirements.txt
git add package.json
git commit -m "Add dependencies"

# 3. Другие установят:
npm install  # для Node.js
pip install -r requirements.txt  # для Python
```

---

## Troubleshooting

### ❓ Что делать если всё сломалось?

**Порядок действий:**

1. **Не паникуйте** - Git почти всегда можно восстановить
2. **Не делайте больше команд** - не усугубляйте ситуацию
3. **Проверьте состояние:**
   ```bash
   git status
   git log --oneline -5
   git reflog
   ```

4. **Если потеряли коммиты:**
   ```bash
   git reflog  # Найти нужный hash
   git checkout <hash>
   git checkout -b recovery-branch
   ```

5. **Если есть конфликты:**
   ```bash
   git status  # Посмотреть какие файлы
   # Открыть файлы, разрешить конфликты
   git add .
   git commit
   ```

6. **Если нужно отменить последнее действие:**
   ```bash
   git reset --hard HEAD@{1}  # Вернуться на 1 действие назад
   ```

✅ **Подробнее:** См. `troubleshooting.md` для детального разбора ошибок.

---

## Полезные ресурсы

### ❓ Где учиться Git?

**Интерактивные туториалы:**
- https://learngitbranching.js.org - визуальное обучение
- https://gitexercises.fracz.com - практические задачи

**Документация:**
- https://git-scm.com/doc - официальная документация
- https://training.github.com - GitHub Learning Lab

**Шпаргалки:**
- https://education.github.com/git-cheat-sheet-education.pdf
- `git-commands-cheatsheet.md` в этом справочнике

**Книги:**
- Pro Git (бесплатная): https://git-scm.com/book/ru/v2

---

### ❓ Какие GUI клиенты для Git существуют?

**Встроенные в IDE:**
- VS Code (встроенный Git)
- IntelliJ IDEA / WebStorm / PyCharm
- Visual Studio

**Standalone приложения:**
- **GitHub Desktop** - простой, для начинающих (Windows/Mac)
- **GitKraken** - красивый, функциональный (кросс-платформенный)
- **Sourcetree** - мощный, от Atlassian (Windows/Mac)
- **Fork** - быстрый, платный (Windows/Mac)
- **TortoiseGit** - интеграция с Explorer (Windows)

💡 **Рекомендация:** Начните с командной строки чтобы понять основы, потом переходите на GUI.

---

## Глоссарий терминов

См. `glossary.md` для подробного словаря всех Git/GitHub терминов.

---

✅ **Не нашли ответ?** Проверьте:
- `troubleshooting.md` - решение проблем
- `git-commands-cheatsheet.md` - все команды с примерами
- `glossary.md` - словарь терминов
