# Glossary - Словарь терминов Git и GitHub

Полный справочник терминов с объяснениями на русском и английском.

---

## A

### **Add (Добавление)**
Процесс добавления изменений в staging area перед коммитом.
```bash
git add file.txt
```

### **Amend (Исправление)**
Изменение последнего коммита (добавление файлов или изменение commit message).
```bash
git commit --amend
```

### **Annotated Tag (Аннотированный тег)**
Тег с полной информацией: автор, дата, сообщение. Рекомендуется для релизов.
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
```

### **Ahead (Впереди)**
Состояние когда локальная ветка содержит коммиты которых нет на remote.
```bash
# Вывод: Your branch is ahead of 'origin/main' by 2 commits
```

---

## B

### **Bare Repository (Голый репозиторий)**
Репозиторий без рабочей директории, только .git содержимое. Используется на серверах.
```bash
git init --bare
```

### **Behind (Позади)**
Состояние когда remote ветка содержит коммиты которых нет локально.
```bash
# Вывод: Your branch is behind 'origin/main' by 3 commits
```

### **Bisect (Бинарный поиск)**
Метод поиска коммита который внёс баг через бинарный поиск.
```bash
git bisect start
git bisect bad    # текущий коммит сломан
git bisect good v1.0.0  # эта версия работала
```

### **Blame (Аннотация авторства)**
Показывает кто и когда изменил каждую строку файла.
```bash
git blame file.txt
```

### **Branch (Ветка)**
Независимая линия разработки. Указатель на коммит.
```bash
git branch feature-login
git checkout feature-login
```

### **Bundle (Бандл)**
Архив репозитория для передачи без сети.
```bash
git bundle create repo.bundle --all
```

---

## C

### **Cache (Кэш)**
Альтернативное название для staging area (область подготовки).
```bash
git rm --cached file.txt  # убрать из staging
```

### **Checkout (Переключение)**
Переключение между ветками или восстановление файлов.
```bash
git checkout main
git checkout -- file.txt  # восстановить файл
```

### **Cherry-pick (Выборочное применение)**
Применение конкретного коммита из одной ветки в другую.
```bash
git cherry-pick abc123
```

### **Clone (Клонирование)**
Создание локальной копии удалённого репозитория.
```bash
git clone https://github.com/user/repo.git
```

### **Commit (Коммит)**
Снимок состояния проекта в определённый момент времени.
```bash
git commit -m "Add feature"
```

### **Commit Hash (Хеш коммита)**
Уникальный идентификатор коммита (40-символьная SHA-1 строка).
```
abc123def456...  # полный hash
abc123           # короткий hash (7 символов)
```

### **Commit Message (Сообщение коммита)**
Описание изменений в коммите.
```
Add user authentication

Implemented login/logout functionality
with JWT tokens.

Fixes #123
```

### **Conflict (Конфликт)**
Ситуация когда одни и те же строки изменены по-разному в разных ветках.
```
<<<<<<< HEAD
console.log("Version A");
=======
console.log("Version B");
>>>>>>> feature
```

### **Credentials (Учётные данные)**
Username и password/token для доступа к remote репозиторию.
```bash
git config --global credential.helper store
```

---

## D

### **Detached HEAD (Отделённый HEAD)**
Состояние когда HEAD указывает на конкретный коммит, а не на ветку.
```bash
git checkout abc123  # detached HEAD state
```

### **Diff (Разница)**
Различия между коммитами, ветками, файлами.
```bash
git diff
git diff main..feature
```

### **Diverged (Расходятся)**
Состояние когда локальная и remote ветки содержат разные коммиты.
```
# Вывод: Your branch and 'origin/main' have diverged
```

---

## F

### **Fast-forward (Быстрая перемотка)**
Тип merge когда просто перемещается указатель ветки (без merge commit).
```bash
git merge --ff-only feature
```

### **Fetch (Загрузка)**
Скачивание изменений из remote репозитория без слияния.
```bash
git fetch origin
```

### **Fork (Форк)**
Копия чужого репозитория на вашем GitHub аккаунте.
```
Original: github.com/user/repo
Fork: github.com/YOUR-USER/repo
```

---

## G

### **Git**
Распределённая система контроля версий.

### **GitHub**
Веб-платформа для хостинга Git репозиториев.

### **GitLab**
Альтернатива GitHub, веб-платформа для Git.

### **Gitignore (.gitignore)**
Файл со списком файлов/папок которые Git должен игнорировать.
```
node_modules/
.env
*.log
```

### **GUI (Графический интерфейс)**
Визуальные программы для работы с Git (GitKraken, GitHub Desktop и т.д.).

---

## H

### **HEAD**
Указатель на текущий коммит (обычно последний коммит текущей ветки).
```bash
HEAD      # текущий коммит
HEAD~1    # предыдущий коммит
HEAD~2    # 2 коммита назад
```

### **Hook (Хук)**
Скрипт который автоматически выполняется при определённых Git событиях.
```bash
# .git/hooks/pre-commit
#!/bin/sh
npm run lint
```

### **HTTPS**
Протокол для доступа к remote репозиториям через URL.
```bash
git clone https://github.com/user/repo.git
```

---

## I

### **Index (Индекс)**
Другое название для staging area.

### **Init (Инициализация)**
Создание нового Git репозитория.
```bash
git init
```

### **Issue (Задача)**
Задача, баг или feature request на GitHub.
```
#123 - Issue номер 123
```

---

## L

### **LFS (Large File Storage)**
Расширение Git для работы с большими файлами.
```bash
git lfs track "*.psd"
```

### **Lightweight Tag (Легковесный тег)**
Простой указатель на коммит без дополнительной информации.
```bash
git tag v1.0.0
```

### **Log (Журнал)**
История коммитов.
```bash
git log
git log --oneline
git log --graph
```

---

## M

### **Main / Master**
Основная ветка репозитория.
- **main** - современное название (с 2020)
- **master** - старое название

### **Merge (Слияние)**
Объединение изменений из одной ветки в другую.
```bash
git merge feature-branch
```

### **Merge Commit (Коммит слияния)**
Специальный коммит создаваемый при merge (имеет двух родителей).

### **Merge Conflict (Конфликт слияния)**
См. Conflict.

---

## O

### **Origin**
Стандартное имя для основного remote репозитория.
```bash
git remote add origin https://github.com/user/repo.git
```

---

## P

### **PAT (Personal Access Token)**
Токен для аутентификации на GitHub вместо пароля.
```
ghp_abc123def456...
```

### **Patch (Патч)**
Файл с diff изменениями который можно применить.
```bash
git diff > changes.patch
git apply changes.patch
```

### **Pull (Получение и слияние)**
Загрузка изменений с remote и слияние с локальной веткой.
```bash
git pull origin main
# Эквивалентно: git fetch + git merge
```

### **Pull Request (PR, Пулл реквест)**
Запрос на слияние изменений из одной ветки в другую (на GitHub).
```
feature-branch → main
```

### **Push (Отправка)**
Отправка локальных коммитов на remote репозиторий.
```bash
git push origin main
```

---

## R

### **Rebase (Перебазирование)**
Перемещение коммитов на другую базу, переписывание истории.
```bash
git rebase main
```

### **Reflog (Журнал ссылок)**
История всех перемещений HEAD (даже удалённые коммиты).
```bash
git reflog
```

### **Remote (Удалённый репозиторий)**
Репозиторий на сервере (GitHub, GitLab и т.д.).
```bash
git remote -v
git remote add origin URL
```

### **Repository (Репозиторий)**
Хранилище проекта с историей изменений.

### **Reset (Сброс)**
Откат коммитов, перемещение HEAD назад.
```bash
git reset --soft HEAD~1   # оставить изменения в staging
git reset --mixed HEAD~1  # оставить в рабочей директории
git reset --hard HEAD~1   # полностью удалить
```

### **Restore (Восстановление)**
Восстановление файлов (новая команда с Git 2.23).
```bash
git restore file.txt             # отменить изменения
git restore --staged file.txt    # убрать из staging
```

### **Revert (Отмена)**
Создание нового коммита отменяющего изменения предыдущего.
```bash
git revert HEAD
```

---

## S

### **SHA (Secure Hash Algorithm)**
Алгоритм хеширования используемый для commit hash.
```
abc123def456789...  # SHA-1 hash
```

### **Shallow Clone (Поверхностное клонирование)**
Клонирование только последних коммитов без полной истории.
```bash
git clone --depth 1 https://github.com/user/repo.git
```

### **Squash (Сжатие)**
Объединение нескольких коммитов в один.
```bash
git rebase -i HEAD~3  # в редакторе: squash
```

### **SSH (Secure Shell)**
Протокол для безопасного доступа к remote репозиториям.
```bash
git clone git@github.com:user/repo.git
```

### **Stage / Staging Area (Область подготовки)**
Промежуточная область между рабочей директорией и репозиторием.
```bash
git add file.txt  # файл попадает в staging area
```

### **Stash (Припрятывание)**
Временное сохранение незакоммиченных изменений.
```bash
git stash
git stash pop
```

### **Status (Статус)**
Состояние рабочей директории и staging area.
```bash
git status
```

### **Submodule (Подмодуль)**
Репозиторий внутри другого репозитория.
```bash
git submodule add https://github.com/user/lib.git libs/lib
```

### **Switch (Переключение)**
Переключение между ветками (новая команда с Git 2.23).
```bash
git switch main
git switch -c new-branch
```

---

## T

### **Tag (Тег)**
Метка на конкретном коммите, обычно для версий релизов.
```bash
git tag v1.0.0
git tag -a v1.0.0 -m "Release 1.0"
```

### **Three-way Merge (Трёхстороннее слияние)**
Merge с использованием общего предка двух веток.

### **Tracking Branch (Отслеживающая ветка)**
Локальная ветка связанная с remote веткой.
```bash
git push -u origin feature  # установить tracking
```

### **Tree (Дерево)**
Структура файлов и директорий в коммите.

---

## U

### **Uncommitted Changes (Незакоммиченные изменения)**
Изменения в рабочей директории которые ещё не в коммите.

### **Untracked Files (Неотслеживаемые файлы)**
Файлы которые Git ещё не отслеживает.
```bash
# git status показывает как:
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        newfile.txt
```

### **Unstaged Changes (Неподготовленные изменения)**
Изменения которые не добавлены в staging area.

### **Upstream (Восходящий поток)**
Исходный репозиторий от которого сделан fork.
```bash
git remote add upstream https://github.com/original/repo.git
```

---

## W

### **Working Directory / Working Tree (Рабочая директория)**
Папка с файлами проекта где вы работаете.

### **Workflow (Рабочий процесс)**
Процесс работы с Git (например: Git Flow, GitHub Flow).

### **Worktree (Рабочее дерево)**
Возможность работать с несколькими ветками одновременно в разных директориях.
```bash
git worktree add ../feature-branch feature
```

---

## Состояния файлов

### **Untracked (Неотслеживаемый)**
Новый файл который Git не отслеживает.
```bash
?? newfile.txt
```

### **Unmodified (Неизменённый)**
Файл в Git, не изменён с последнего коммита.

### **Modified (Изменённый)**
Файл изменён но не добавлен в staging.
```bash
M  file.txt
```

### **Staged (Подготовленный)**
Файл добавлен в staging area, готов к коммиту.
```bash
A  newfile.txt
```

### **Committed (Закоммиченный)**
Изменения сохранены в истории репозитория.

---

## Типы изменений в git status

| Обозначение | Значение | Расшифровка |
|------------|----------|-------------|
| `??` | Untracked | Неотслеживаемый файл |
| `A` | Added | Добавлен в Git |
| `M` | Modified | Изменён |
| `D` | Deleted | Удалён |
| `R` | Renamed | Переименован |
| `C` | Copied | Скопирован |
| `U` | Unmerged | Не слит (конфликт) |

---

## GitHub специфичные термины

### **Actions (Действия)**
CI/CD платформа встроенная в GitHub.
```yaml
# .github/workflows/test.yml
name: Tests
on: [push]
```

### **Assignee (Назначенный)**
Пользователь назначенный на issue или PR.

### **Code Review (Ревью кода)**
Процесс проверки кода другими разработчиками.

### **Collaborator (Соавтор)**
Пользователь с правами на запись в репозиторий.

### **Contributor (Контрибьютор)**
Человек который внёс вклад в проект.

### **Dependabot**
Бот GitHub для автоматического обновления зависимостей.

### **Gist**
Небольшой сниппет кода на GitHub.
```
https://gist.github.com/user/abc123
```

### **Label (Метка)**
Категоризация issues и PR (bug, feature, help wanted и т.д.).

### **Markdown**
Язык разметки используемый для README, issues, PR и т.д.
```markdown
# Заголовок
**Bold text**
- List item
```

### **Milestone (Веха)**
Группа issues/PR для конкретной цели или версии.

### **Organization (Организация)**
Аккаунт GitHub для команд и компаний.

### **Pages (GitHub Pages)**
Хостинг статических сайтов на GitHub.
```
https://username.github.io/repo
```

### **Project (Проект)**
Канбан-доска для управления задачами на GitHub.

### **Protected Branch (Защищённая ветка)**
Ветка с ограничениями (требуется review, CI должен пройти и т.д.).

### **README.md**
Файл с описанием проекта (отображается на главной странице репозитория).

### **Release (Релиз)**
Официальная версия проекта с бинарниками и changelog.
```
v1.0.0 - Initial Release
```

### **Repository (Репозиторий)**
Проект на GitHub.

### **Star (Звезда)**
Закладка понравившегося репозитория.

### **Watch (Отслеживание)**
Подписка на уведомления о новых issues/PR в репозитории.

### **Wiki**
Документация для репозитория на GitHub.

---

## Рабочие процессы (Workflows)

### **Git Flow**
Workflow с ветками: main, develop, feature, release, hotfix.

### **GitHub Flow**
Простой workflow: main + feature branches + Pull Requests.

### **Trunk-Based Development**
Разработка в одной ветке (main/trunk) с короткоживущими feature ветками.

---

## Протоколы

### **HTTPS (HyperText Transfer Protocol Secure)**
```
https://github.com/user/repo.git
```
**Плюсы:** Работает везде, легко настроить
**Минусы:** Нужен PAT, вводить credentials

### **SSH (Secure Shell)**
```
git@github.com:user/repo.git
```
**Плюсы:** Не нужен PAT, безопасно
**Минусы:** Нужно настраивать SSH ключи

### **Git Protocol**
```
git://github.com/user/repo.git
```
**Редко используется:** Только для чтения, не зашифрован.

---

## Популярные флаги команд

### **-a (all)**
```bash
git add -a       # добавить все изменения
git commit -a    # закоммитить все tracked файлы
git push --all   # push всех веток
```

### **-b (branch)**
```bash
git checkout -b feature  # создать и переключиться на ветку
git push -u origin -b    # установить upstream
```

### **-d / -D (delete)**
```bash
git branch -d feature    # удалить ветку (безопасно)
git branch -D feature    # принудительно удалить
```

### **-f / --force**
```bash
git push --force         # принудительный push (опасно!)
```

### **--force-with-lease**
```bash
git push --force-with-lease  # безопасная версия --force
```

### **-i (interactive)**
```bash
git add -i              # интерактивное добавление
git rebase -i HEAD~3    # интерактивный rebase
```

### **-m (message)**
```bash
git commit -m "Message"  # коммит с сообщением
git tag -m "Tag message" # тег с сообщением
```

### **-u (set-upstream)**
```bash
git push -u origin main  # установить tracking branch
```

### **-v (verbose)**
```bash
git remote -v           # показать URLs
git branch -v           # показать последний коммит в ветках
```

---

## Сокращения Git команд

Можно использовать сокращения вместо полных команд:

| Полная команда | Сокращение |
|---------------|------------|
| `git status` | `git st` (если настроен alias) |
| `git checkout` | `git co` (если настроен alias) |
| `git commit` | `git ci` (если настроен alias) |
| `git branch` | `git br` (если настроен alias) |

**Настроить aliases:**
```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.ci commit
git config --global alias.br branch
```

---

## Операторы ссылок

### **HEAD^**
Первый родитель коммита (используется для merge коммитов).
```bash
HEAD^   # первый родитель
HEAD^2  # второй родитель
```

### **HEAD~**
N-ный предок по первому родителю.
```bash
HEAD~1  # 1 коммит назад
HEAD~2  # 2 коммита назад
HEAD~3  # 3 коммита назад
```

### **@**
Сокращение для HEAD (в Git 2.0+).
```bash
git show @       # то же что git show HEAD
git diff @~3     # то же что git diff HEAD~3
```

### **..**
Диапазон коммитов (exclusive).
```bash
git log main..feature  # коммиты в feature но не в main
```

### **...**
Диапазон коммитов (symmetric difference).
```bash
git log main...feature  # коммиты уникальные для каждой ветки
```

---

## Распространённые аббревиатуры

| Аббревиатура | Расшифровка |
|-------------|-------------|
| **CI/CD** | Continuous Integration / Continuous Deployment |
| **CLI** | Command Line Interface |
| **CRLF** | Carriage Return Line Feed (Windows) |
| **GUI** | Graphical User Interface |
| **IDE** | Integrated Development Environment |
| **LF** | Line Feed (Unix/Linux/Mac) |
| **LFS** | Large File Storage |
| **MR** | Merge Request (GitLab термин для PR) |
| **OSS** | Open Source Software |
| **PAT** | Personal Access Token |
| **PR** | Pull Request |
| **SHA** | Secure Hash Algorithm |
| **SSH** | Secure Shell |
| **URL** | Uniform Resource Locator |
| **VCS** | Version Control System |
| **WIP** | Work In Progress |

---

## Emoji в Git коммитах

Популярные emoji для категоризации коммитов (Gitmoji):

| Emoji | Код | Значение |
|-------|-----|----------|
| ✨ | `:sparkles:` | Новая функция |
| 🐛 | `:bug:` | Исправление бага |
| 📝 | `:memo:` | Документация |
| 🚀 | `:rocket:` | Деплой |
| 💄 | `:lipstick:` | UI/Стили |
| ♻️ | `:recycle:` | Рефакторинг |
| ⚡️ | `:zap:` | Оптимизация |
| 🔒 | `:lock:` | Безопасность |
| ⬆️ | `:arrow_up:` | Обновление зависимостей |
| 🔥 | `:fire:` | Удаление кода |
| ✅ | `:white_check_mark:` | Добавление тестов |

**Пример:**
```bash
git commit -m "✨ Add user authentication"
git commit -m ":sparkles: Add user authentication"
```

---

## Конфигурационные файлы

### **.git/**
Директория с внутренними данными Git (история, конфигурация, hooks).

### **.gitignore**
Файлы которые Git игнорирует.
```
node_modules/
.env
*.log
```

### **.gitattributes**
Настройки для конкретных файлов (line endings, diff, merge).
```
* text=auto
*.js text eol=lf
*.bat text eol=crlf
```

### **.gitkeep**
Пустой файл для коммита пустых директорий (Git не отслеживает пустые папки).

### **README.md**
Описание проекта.

### **LICENSE**
Лицензия проекта (MIT, GPL, Apache и т.д.).

### **CONTRIBUTING.md**
Руководство для контрибьюторов.

### **CODE_OF_CONDUCT.md**
Кодекс поведения в проекте.

### **CHANGELOG.md**
История изменений версий.

---

## Уровни конфигурации Git

| Уровень | Область действия | Файл |
|---------|-----------------|------|
| **--system** | Все пользователи системы | `/etc/gitconfig` |
| **--global** | Текущий пользователь | `~/.gitconfig` |
| **--local** | Конкретный репозиторий | `.git/config` |

**Приоритет:** local → global → system

```bash
git config --local user.name "Work Name"
git config --global user.name "Personal Name"
```

---

## Жизненный цикл файла в Git

```
Untracked → Staged → Committed
    ↓          ↓          ↓
[git add] [git commit] [history]
    ↑          ↑
Modified ← Unmodified
```

**Детальный цикл:**
1. **Untracked** - новый файл
2. `git add` → **Staged** (в staging area)
3. `git commit` → **Committed** (в истории)
4. Изменили файл → **Modified** (изменён но не staged)
5. `git add` → **Staged** снова
6. `git commit` → **Committed** новая версия

---

## Структура коммита

```
Commit Object
├── Tree (snapshot файлов)
├── Parent commit(s)
├── Author
├── Committer
├── Timestamp
└── Message
```

**Пример:**
```
commit abc123def456
Author: Suheil <suheil@example.com>
Date:   Mon Feb 4 10:00:00 2026 +0400

    Add user authentication

    Implemented JWT-based login system
    with password hashing.

    Fixes #123
```

---

## Полезные команды с терминами

```bash
# Repository
git init                    # инициализация
git clone URL               # клонирование

# Changes
git status                  # статус
git diff                    # различия
git add file.txt            # staging
git commit -m "Message"     # коммит

# Branches
git branch                  # список веток
git checkout -b feature     # создать и переключиться
git merge feature           # слияние

# Remote
git remote -v               # список remotes
git push origin main        # отправка
git pull origin main        # получение и слияние
git fetch origin            # только получение

# History
git log                     # журнал коммитов
git reflog                  # журнал HEAD
git blame file.txt          # авторство строк

# Undo
git reset HEAD~1            # откат коммита
git revert HEAD             # отмена коммита (новым коммитом)
git restore file.txt        # восстановление файла
```

---

✅ **Этот глоссарий покрывает 95%+ терминов которые встретятся при работе с Git и GitHub!**

Используйте Ctrl+F для быстрого поиска нужного термина.
