# Git Commands Cheatsheet

Полная шпаргалка команд Git с примерами и описаниями.

---

## Setup и Config

### `git config`
**Назначение:** Настройка конфигурации Git
**Использование:** `git config [--global|--local|--system] <key> <value>`

**Примеры:**
- `git config --global user.name "Суxейль"` — установка имени пользователя глобально
- `git config --global user.email "suheil@example.com"` — установка email
- `git config --list` — просмотр всех настроек
- `git config --global --list` — просмотр глобальных настроек
- `git config user.name` — просмотр конкретной настройки
- `git config --global core.editor "code --wait"` — установка VS Code как редактора
- `git config --global core.autocrlf true` — автоконвертация CRLF/LF (для Windows)
- `git config --global init.defaultBranch main` — установка main как дефолтной ветки
- `git config --global credential.helper store` — сохранение credentials

**Уровни конфигурации:**
- `--system` — для всех пользователей системы
- `--global` — для текущего пользователя
- `--local` — для конкретного репозитория (по умолчанию)

### `git help`
**Назначение:** Получение справки по командам
**Использование:** `git help <command>`

**Примеры:**
- `git help` — список основных команд
- `git help commit` — подробная справка по commit
- `git help -a` — список всех доступных команд
- `git help -g` — список руководств
- `git commit --help` — альтернативный способ получить справку

### `git version`
**Назначение:** Проверка версии Git
**Использование:** `git version`

**Примеры:**
- `git version` — показать установленную версию Git
- `git --version` — альтернативный синтаксис

---

## Creating Repositories

### `git init`
**Назначение:** Инициализация нового Git репозитория
**Использование:** `git init [directory]`

**Примеры:**
- `git init` — создание репозитория в текущей директории
- `git init my-project` — создание репозитория в новой папке
- `git init --bare` — создание bare репозитория (без рабочей директории)
- `git init --initial-branch=main` — инициализация с веткой main

### `git clone`
**Назначение:** Клонирование существующего репозитория
**Использование:** `git clone <url> [directory]`

**Примеры:**
- `git clone https://github.com/user/repo.git` — клонирование по HTTPS
- `git clone git@github.com:user/repo.git` — клонирование по SSH
- `git clone https://github.com/user/repo.git my-folder` — клонирование в конкретную папку
- `git clone --depth 1 https://github.com/user/repo.git` — shallow clone (только последний коммит)
- `git clone --branch develop https://github.com/user/repo.git` — клонирование конкретной ветки
- `git clone --recursive https://github.com/user/repo.git` — клонирование с submodules

---

## Making Changes

### `git status`
**Назначение:** Просмотр состояния рабочей директории
**Использование:** `git status [options]`

**Примеры:**
- `git status` — подробный статус
- `git status -s` — краткий статус (short format)
- `git status -sb` — краткий статус с информацией о ветке
- `git status --ignored` — показать игнорируемые файлы
- `git status -uno` — не показывать untracked файлы

**Обозначения в кратком формате:**
- `??` — untracked файл
- `A` — added (добавлен в staging)
- `M` — modified (изменён)
- `D` — deleted (удалён)
- `R` — renamed (переименован)

### `git add`
**Назначение:** Добавление изменений в staging area
**Использование:** `git add <files>`

**Примеры:**
- `git add file.txt` — добавить конкретный файл
- `git add .` — добавить все изменения в текущей директории
- `git add -A` — добавить все изменения в репозитории
- `git add *.js` — добавить все файлы .js
- `git add src/` — добавить все файлы в папке src
- `git add -p` — интерактивное добавление (по частям)
- `git add -u` — добавить только изменённые и удалённые файлы (не новые)

### `git commit`
**Назначение:** Сохранение изменений в репозитории
**Использование:** `git commit [options]`

**Примеры:**
- `git commit -m "Добавил новую функцию"` — коммит с сообщением
- `git commit` — открыть редактор для написания сообщения
- `git commit -am "Исправил баг"` — add + commit для отслеживаемых файлов
- `git commit --amend` — изменить последний коммит
- `git commit --amend -m "Новое сообщение"` — изменить сообщение последнего коммита
- `git commit --amend --no-edit` — добавить изменения в последний коммит без изменения сообщения
- `git commit --allow-empty -m "Пустой коммит"` — создать коммит без изменений
- `git commit -v` — показать diff в редакторе при создании коммита

**Хорошие практики commit message:**
```
Краткое описание изменения (до 50 символов)

Подробное описание (если нужно):
- Что было изменено
- Почему было изменено
- Какие есть побочные эффекты
```

### `git diff`
**Назначение:** Просмотр изменений
**Использование:** `git diff [options]`

**Примеры:**
- `git diff` — изменения в рабочей директории (не в staging)
- `git diff --staged` — изменения в staging area
- `git diff HEAD` — все изменения (рабочая директория + staging)
- `git diff branch1 branch2` — различия между ветками
- `git diff commit1 commit2` — различия между коммитами
- `git diff file.txt` — изменения в конкретном файле
- `git diff --stat` — краткая статистика изменений
- `git diff --color-words` — показать изменения по словам, а не по строкам
- `git diff HEAD~3 HEAD` — изменения за последние 3 коммита

### `git rm`
**Назначение:** Удаление файлов из репозитория
**Использование:** `git rm <file>`

**Примеры:**
- `git rm file.txt` — удалить файл из Git и файловой системы
- `git rm --cached file.txt` — удалить файл из Git, но оставить локально
- `git rm -r directory/` — удалить директорию рекурсивно
- `git rm --cached -r node_modules/` — убрать node_modules из отслеживания
- `git rm -f file.txt` — принудительное удаление (если файл в staging)

### `git mv`
**Назначение:** Перемещение или переименование файлов
**Использование:** `git mv <source> <destination>`

**Примеры:**
- `git mv old-name.txt new-name.txt` — переименовать файл
- `git mv file.txt directory/` — переместить файл в директорию
- `git mv src/old.js src/new.js` — переименовать с путём

**Эквивалентно:**
```bash
mv old-name.txt new-name.txt
git rm old-name.txt
git add new-name.txt
```

---

## Branching и Merging

### `git branch`
**Назначение:** Управление ветками
**Использование:** `git branch [options] [branch-name]`

**Примеры:**
- `git branch` — список локальных веток
- `git branch -a` — список всех веток (локальных и удалённых)
- `git branch -r` — список удалённых веток
- `git branch new-feature` — создать новую ветку
- `git branch -d feature-branch` — удалить ветку (безопасно)
- `git branch -D feature-branch` — принудительно удалить ветку
- `git branch -m old-name new-name` — переименовать ветку
- `git branch -m new-name` — переименовать текущую ветку
- `git branch -v` — показать последний коммит в каждой ветке
- `git branch --merged` — список веток, слитых в текущую
- `git branch --no-merged` — список веток, не слитых в текущую
- `git branch --contains <commit>` — ветки, содержащие конкретный коммит

### `git checkout`
**Назначение:** Переключение между ветками или восстановление файлов
**Использование:** `git checkout <branch|commit|file>`

**Примеры:**
- `git checkout main` — переключиться на ветку main
- `git checkout -b new-feature` — создать и переключиться на новую ветку
- `git checkout -b feature origin/feature` — создать локальную ветку из удалённой
- `git checkout -- file.txt` — отменить изменения в файле
- `git checkout .` — отменить все изменения в рабочей директории
- `git checkout <commit-hash>` — переключиться на конкретный коммит (detached HEAD)
- `git checkout <commit-hash> file.txt` — восстановить файл из коммита
- `git checkout -` — переключиться на предыдущую ветку

⚠️ **Внимание:** `git checkout` — универсальная команда. В новых версиях Git рекомендуется использовать `git switch` и `git restore`.

### `git switch`
**Назначение:** Переключение между ветками (новая команда с Git 2.23)
**Использование:** `git switch <branch>`

**Примеры:**
- `git switch main` — переключиться на ветку main
- `git switch -c new-feature` — создать и переключиться на новую ветку
- `git switch -` — переключиться на предыдущую ветку
- `git switch --detach <commit>` — переключиться на коммит (detached HEAD)

### `git restore`
**Назначение:** Восстановление файлов (новая команда с Git 2.23)
**Использование:** `git restore [options] <file>`

**Примеры:**
- `git restore file.txt` — отменить изменения в файле
- `git restore .` — отменить все изменения
- `git restore --staged file.txt` — убрать файл из staging
- `git restore --source=HEAD~2 file.txt` — восстановить файл из коммита 2 назад

### `git merge`
**Назначение:** Слияние веток
**Использование:** `git merge <branch>`

**Примеры:**
- `git merge feature-branch` — слить feature-branch в текущую ветку
- `git merge --no-ff feature-branch` — слияние без fast-forward (создаст merge commit)
- `git merge --squash feature-branch` — слить все коммиты в один
- `git merge --abort` — отменить слияние при конфликте
- `git merge --continue` — продолжить слияние после разрешения конфликтов
- `git merge -X theirs feature-branch` — при конфликтах брать версию из feature-branch
- `git merge -X ours feature-branch` — при конфликтах брать версию из текущей ветки

**Типы слияния:**
- **Fast-forward:** Простое перемещение указателя ветки (нет divergence)
- **3-way merge:** Создание merge commit (есть divergence)
- **Squash:** Все коммиты ветки в один коммит

### `git rebase`
**Назначение:** Перебазирование коммитов
**Использование:** `git rebase <branch>`

**Примеры:**
- `git rebase main` — перебазировать текущую ветку на main
- `git rebase --interactive HEAD~3` — интерактивное редактирование последних 3 коммитов
- `git rebase -i HEAD~3` — краткая форма
- `git rebase --abort` — отменить rebase
- `git rebase --continue` — продолжить rebase после разрешения конфликтов
- `git rebase --skip` — пропустить текущий коммит при rebase
- `git rebase --onto main feature-branch bugfix` — перебазировать bugfix с feature-branch на main

**Интерактивный rebase команды:**
- `pick` — оставить коммит как есть
- `reword` — изменить commit message
- `edit` — остановиться для редактирования коммита
- `squash` — объединить с предыдущим коммитом
- `fixup` — объединить с предыдущим, отбросив message
- `drop` — удалить коммит

⚠️ **Внимание:** Не делайте rebase для коммитов, которые уже push'нуты в публичный репозиторий!

### `git cherry-pick`
**Назначение:** Применение конкретного коммита к текущей ветке
**Использование:** `git cherry-pick <commit>`

**Примеры:**
- `git cherry-pick abc123` — применить коммит abc123
- `git cherry-pick abc123 def456` — применить несколько коммитов
- `git cherry-pick main~3` — применить 3-й коммит от конца main
- `git cherry-pick --abort` — отменить cherry-pick
- `git cherry-pick --continue` — продолжить после разрешения конфликтов
- `git cherry-pick -n abc123` — применить изменения без создания коммита

---

## Remote Repositories

### `git remote`
**Назначение:** Управление удалёнными репозиториями
**Использование:** `git remote [options]`

**Примеры:**
- `git remote` — список удалённых репозиториев
- `git remote -v` — список с URL
- `git remote add origin https://github.com/user/repo.git` — добавить удалённый репозиторий
- `git remote remove origin` — удалить удалённый репозиторий
- `git remote rename origin upstream` — переименовать удалённый репозиторий
- `git remote show origin` — подробная информация об удалённом репозитории
- `git remote set-url origin git@github.com:user/repo.git` — изменить URL
- `git remote prune origin` — удалить ссылки на удалённые ветки, которые были удалены

### `git fetch`
**Назначение:** Загрузка изменений из удалённого репозитория
**Использование:** `git fetch [remote] [branch]`

**Примеры:**
- `git fetch` — загрузить изменения из origin
- `git fetch origin` — загрузить изменения из origin
- `git fetch origin main` — загрузить изменения только ветки main
- `git fetch --all` — загрузить изменения из всех удалённых репозиториев
- `git fetch --prune` — удалить ссылки на удалённые ветки, которые были удалены
- `git fetch -p` — краткая форма --prune

⚠️ **Важно:** `fetch` только загружает изменения, но не сливает их с локальными ветками.

### `git pull`
**Назначение:** Загрузка и слияние изменений
**Использование:** `git pull [remote] [branch]`

**Примеры:**
- `git pull` — fetch + merge из tracking branch
- `git pull origin main` — загрузить и слить main из origin
- `git pull --rebase` — fetch + rebase вместо merge
- `git pull --ff-only` — только fast-forward merge
- `git pull --all` — загрузить изменения из всех удалённых репозиториев
- `git pull -p` — с удалением устаревших ссылок

**Эквивалентно:**
```bash
git fetch origin
git merge origin/main
```

### `git push`
**Назначение:** Отправка изменений в удалённый репозиторий
**Использование:** `git push [remote] [branch]`

**Примеры:**
- `git push` — отправить текущую ветку в tracking branch
- `git push origin main` — отправить ветку main в origin
- `git push -u origin feature-branch` — отправить и установить tracking
- `git push --all` — отправить все ветки
- `git push --tags` — отправить все теги
- `git push origin --delete feature-branch` — удалить удалённую ветку
- `git push origin :feature-branch` — альтернативный способ удаления ветки
- `git push --force` — принудительная отправка (перезаписывает историю)
- `git push --force-with-lease` — безопасная принудительная отправка

⚠️ **Внимание:** `--force` опасен! Используйте `--force-with-lease` вместо него.

---

## Inspection и Comparison

### `git log`
**Назначение:** Просмотр истории коммитов
**Использование:** `git log [options]`

**Примеры:**
- `git log` — полная история коммитов
- `git log --oneline` — краткая история (по одной строке)
- `git log --graph` — графическое представление веток
- `git log --all` — история всех веток
- `git log --oneline --graph --all` — компактный граф всех веток
- `git log -n 5` — последние 5 коммитов
- `git log --since="2 weeks ago"` — коммиты за последние 2 недели
- `git log --until="2024-01-01"` — коммиты до даты
- `git log --author="Суxейль"` — коммиты конкретного автора
- `git log --grep="fix"` — коммиты с "fix" в сообщении
- `git log -S "function_name"` — коммиты, изменившие строку
- `git log --stat` — с статистикой изменений
- `git log -p` — с полным diff
- `git log --follow file.txt` — история конкретного файла (включая переименования)
- `git log main..feature` — коммиты в feature, но не в main
- `git log --pretty=format:"%h - %an, %ar : %s"` — кастомный формат

**Полезные форматы:**
- `%H` — полный hash коммита
- `%h` — короткий hash
- `%an` — имя автора
- `%ae` — email автора
- `%ad` — дата автора
- `%ar` — относительная дата (2 days ago)
- `%s` — subject (первая строка commit message)

### `git show`
**Назначение:** Просмотр информации о коммите
**Использование:** `git show [commit]`

**Примеры:**
- `git show` — показать последний коммит
- `git show abc123` — показать коммит abc123
- `git show HEAD~2` — показать 2-й коммит от конца
- `git show main:file.txt` — показать содержимое файла в ветке main
- `git show --stat` — краткая статистика изменений
- `git show --name-only` — только имена изменённых файлов

### `git blame`
**Назначение:** Показать, кто и когда изменил каждую строку файла
**Использование:** `git blame <file>`

**Примеры:**
- `git blame file.txt` — аннотация всего файла
- `git blame -L 10,20 file.txt` — аннотация строк 10-20
- `git blame -w file.txt` — игнорировать изменения пробелов
- `git blame -C file.txt` — отслеживать перемещения кода между файлами

### `git reflog`
**Назначение:** Журнал всех изменений HEAD
**Использование:** `git reflog [options]`

**Примеры:**
- `git reflog` — история перемещений HEAD
- `git reflog show main` — история ветки main
- `git reflog --all` — история всех ссылок
- `git reflog expire --expire=now --all` — очистить reflog

⚠️ **Полезно:** Reflog спасает при случайном удалении коммитов!

### `git shortlog`
**Назначение:** Сводка коммитов по авторам
**Использование:** `git shortlog [options]`

**Примеры:**
- `git shortlog` — группировка коммитов по авторам
- `git shortlog -sn` — количество коммитов каждого автора (отсортировано)
- `git shortlog --since="1 month ago"` — за последний месяц

### `git describe`
**Назначение:** Описание коммита относительно ближайшего тега
**Использование:** `git describe [options]`

**Примеры:**
- `git describe` — описание текущего коммита
- `git describe --tags` — включая легковесные теги
- `git describe --abbrev=0` — только имя тега (без дополнительной информации)

---

## Undoing Changes

### `git reset`
**Назначение:** Откат коммитов или изменений
**Использование:** `git reset [--soft|--mixed|--hard] <commit>`

**Примеры:**
- `git reset HEAD file.txt` — убрать файл из staging
- `git reset --soft HEAD~1` — отменить последний коммит, оставив изменения в staging
- `git reset --mixed HEAD~1` — отменить последний коммит, оставив изменения в рабочей директории
- `git reset --hard HEAD~1` — полностью удалить последний коммит
- `git reset --hard origin/main` — сбросить ветку до состояния на удалённом репозитории
- `git reset abc123` — откатить до коммита abc123

**Режимы:**
- `--soft` — изменения остаются в staging
- `--mixed` (по умолчанию) — изменения остаются в рабочей директории
- `--hard` — изменения полностью удаляются

⚠️ **Внимание:** `--hard` необратимо удаляет изменения!

### `git revert`
**Назначение:** Создание нового коммита, отменяющего изменения
**Использование:** `git revert <commit>`

**Примеры:**
- `git revert HEAD` — создать коммит, отменяющий последний коммит
- `git revert abc123` — отменить коммит abc123
- `git revert HEAD~3..HEAD` — отменить последние 3 коммита
- `git revert --no-commit HEAD~3..HEAD` — отменить без автоматических коммитов
- `git revert --abort` — отменить процесс revert

⚠️ **Преимущество:** В отличие от reset, не меняет историю. Безопасно для публичных веток.

### `git clean`
**Назначение:** Удаление untracked файлов
**Использование:** `git clean [options]`

**Примеры:**
- `git clean -n` — показать, что будет удалено (dry run)
- `git clean -f` — удалить untracked файлы
- `git clean -fd` — удалить untracked файлы и директории
- `git clean -fX` — удалить только игнорируемые файлы
- `git clean -fx` — удалить untracked и игнорируемые файлы
- `git clean -i` — интерактивный режим

⚠️ **Внимание:** Всегда используйте `-n` перед `-f` для проверки!

---

## Stashing

### `git stash`
**Назначение:** Временное сохранение незакоммиченных изменений
**Использование:** `git stash [options]`

**Примеры:**
- `git stash` — сохранить изменения
- `git stash save "WIP: feature X"` — сохранить с сообщением
- `git stash -u` — включая untracked файлы
- `git stash -a` — включая untracked и ignored файлы
- `git stash list` — список всех stash
- `git stash show` — показать изменения в последнем stash
- `git stash show -p` — показать полный diff
- `git stash show stash@{1}` — показать конкретный stash
- `git stash pop` — применить и удалить последний stash
- `git stash apply` — применить последний stash (не удаляя)
- `git stash apply stash@{2}` — применить конкретный stash
- `git stash drop` — удалить последний stash
- `git stash drop stash@{1}` — удалить конкретный stash
- `git stash clear` — удалить все stash
- `git stash branch feature-branch` — создать ветку из stash

**Формат stash:**
- `stash@{0}` — последний stash
- `stash@{1}` — предпоследний stash
- и т.д.

---

## Tagging

### `git tag`
**Назначение:** Управление тегами (метками релизов)
**Использование:** `git tag [options] [tagname]`

**Примеры:**
- `git tag` — список всех тегов
- `git tag v1.0.0` — создать легковесный тег
- `git tag -a v1.0.0 -m "Release version 1.0.0"` — создать аннотированный тег
- `git tag -a v1.0.0 abc123` — создать тег для конкретного коммита
- `git tag -d v1.0.0` — удалить локальный тег
- `git push origin v1.0.0` — отправить тег на удалённый репозиторий
- `git push origin --tags` — отправить все теги
- `git push origin --delete v1.0.0` — удалить удалённый тег
- `git tag -l "v1.*"` — список тегов по паттерну
- `git show v1.0.0` — показать информацию о теге

**Типы тегов:**
- **Легковесные:** Просто указатель на коммит
- **Аннотированные:** Полноценный объект Git с автором, датой, сообщением

✅ **Рекомендация:** Используйте аннотированные теги для релизов.

---

## Advanced Commands

### `git bisect`
**Назначение:** Бинарный поиск коммита, внесшего баг
**Использование:** `git bisect <subcommand>`

**Примеры:**
- `git bisect start` — начать bisect
- `git bisect bad` — отметить текущий коммит как плохой
- `git bisect good abc123` — отметить коммит как хороший
- `git bisect reset` — завершить bisect и вернуться на исходную ветку
- `git bisect skip` — пропустить текущий коммит

**Типичный workflow:**
```bash
git bisect start
git bisect bad                # текущий коммит сломан
git bisect good v1.0.0        # коммит v1.0.0 работал
# Git переключает на средний коммит
# Тестируете...
git bisect good               # если работает
# или
git bisect bad                # если сломано
# Повторяете, пока Git не найдёт проблемный коммит
git bisect reset
```

### `git submodule`
**Назначение:** Управление подмодулями (вложенными репозиториями)
**Использование:** `git submodule <subcommand>`

**Примеры:**
- `git submodule add https://github.com/user/repo.git path/to/submodule` — добавить подмодуль
- `git submodule init` — инициализировать подмодули
- `git submodule update` — обновить подмодули
- `git submodule update --init --recursive` — инициализировать и обновить все подмодули
- `git submodule foreach git pull origin main` — выполнить команду в каждом подмодуле
- `git submodule deinit path/to/submodule` — деинициализировать подмодуль
- `git submodule status` — статус подмодулей

### `git worktree`
**Назначение:** Управление несколькими рабочими директориями
**Использование:** `git worktree <subcommand>`

**Примеры:**
- `git worktree add ../feature-branch feature-branch` — создать новую рабочую директорию
- `git worktree add -b hotfix ../hotfix main` — создать ветку и рабочую директорию
- `git worktree list` — список всех рабочих директорий
- `git worktree remove ../feature-branch` — удалить рабочую директорию
- `git worktree prune` — очистить устаревшие worktrees

**Применение:** Работа над несколькими ветками одновременно без переключения.

### `git archive`
**Назначение:** Создание архива репозитория
**Использование:** `git archive [options] <tree-ish>`

**Примеры:**
- `git archive --format=zip --output=project.zip HEAD` — создать zip архив
- `git archive --format=tar HEAD | gzip > project.tar.gz` — создать tar.gz архив
- `git archive --format=zip --output=v1.0.0.zip v1.0.0` — архив конкретного тега
- `git archive --format=zip HEAD:src/ > src.zip` — архив конкретной директории

### `git filter-branch`
**Назначение:** Переписывание истории Git
**Использование:** `git filter-branch [options]`

⚠️ **Устарело:** Используйте `git filter-repo` вместо этого.

**Примеры:**
- `git filter-branch --tree-filter 'rm -f passwords.txt' HEAD` — удалить файл из всей истории
- `git filter-branch --subdirectory-filter subdir HEAD` — сделать поддиректорию корнем

### `git filter-repo`
**Назначение:** Современный инструмент для переписывания истории
**Использование:** `git filter-repo [options]`

**Примеры:**
- `git filter-repo --path src/ --path-rename src/:` — оставить только директорию src
- `git filter-repo --invert-paths --path passwords.txt` — удалить файл из истории
- `git filter-repo --mailmap mailmap.txt` — изменить имена и email авторов

⚠️ **Внимание:** Требует установки отдельно. Не входит в стандартный Git.

### `git grep`
**Назначение:** Поиск по содержимому файлов в репозитории
**Использование:** `git grep [options] <pattern>`

**Примеры:**
- `git grep "function_name"` — поиск строки
- `git grep -n "TODO"` — поиск с номерами строк
- `git grep --count "import"` — количество совпадений в каждом файле
- `git grep "pattern" HEAD~3` — поиск в конкретном коммите
- `git grep -e "pattern1" --and -e "pattern2"` — поиск с условием AND
- `git grep -i "pattern"` — регистронезависимый поиск

### `git fsck`
**Назначение:** Проверка целостности репозитория
**Использование:** `git fsck [options]`

**Примеры:**
- `git fsck` — проверка целостности
- `git fsck --full` — полная проверка
- `git fsck --unreachable` — показать недостижимые объекты

### `git gc`
**Назначение:** Сборка мусора и оптимизация репозитория
**Использование:** `git gc [options]`

**Примеры:**
- `git gc` — базовая очистка
- `git gc --aggressive` — агрессивная оптимизация
- `git gc --prune=now` — удалить недостижимые объекты немедленно

### `git prune`
**Назначение:** Удаление недостижимых объектов
**Использование:** `git prune [options]`

**Примеры:**
- `git prune` — удалить недостижимые объекты старше 2 недель
- `git prune --dry-run` — показать, что будет удалено
- `git prune --expire=now` — удалить всё немедленно

### `git bundle`
**Назначение:** Создание бандла для передачи репозитория без сети
**Использование:** `git bundle <subcommand>`

**Примеры:**
- `git bundle create repo.bundle --all` — создать бандл всего репозитория
- `git bundle create commits.bundle HEAD~10..HEAD` — бандл последних 10 коммитов
- `git bundle verify repo.bundle` — проверить бандл
- `git clone repo.bundle local-repo` — клонировать из бандла

### `git notes`
**Назначение:** Добавление заметок к коммитам
**Использование:** `git notes <subcommand>`

**Примеры:**
- `git notes add -m "Important note"` — добавить заметку к последнему коммиту
- `git notes show` — показать заметку
- `git notes remove` — удалить заметку
- `git log --show-notes` — показать заметки в логе

### `git rerere`
**Назначение:** Повторное использование записанных разрешений конфликтов
**Использование:** `git rerere [options]`

**Примеры:**
- `git config --global rerere.enabled true` — включить rerere глобально
- `git rerere status` — статус сохранённых разрешений
- `git rerere diff` — показать, что будет применено
- `git rerere clear` — очистить сохранённые разрешения

**Применение:** Git запоминает, как вы разрешали конфликты, и применяет те же решения при повторных конфликтах.

### `git lfs`
**Назначение:** Git Large File Storage для больших файлов
**Использование:** `git lfs <subcommand>`

**Примеры:**
- `git lfs install` — установить Git LFS для репозитория
- `git lfs track "*.psd"` — отслеживать файлы .psd через LFS
- `git lfs ls-files` — список файлов в LFS
- `git lfs pull` — скачать LFS файлы
- `git lfs prune` — удалить старые LFS объекты

⚠️ **Внимание:** Требует установки Git LFS отдельно.

---

## Git Aliases (Псевдонимы)

Создание собственных сокращений команд:

```bash
# Основные алиасы
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status

# Полезные алиасы
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual 'log --oneline --graph --all'
git config --global alias.amend 'commit --amend --no-edit'
git config --global alias.undo 'reset --soft HEAD~1'

# Продвинутые алиасы
git config --global alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
```

**Использование:**
```bash
git co main          # вместо git checkout main
git br               # вместо git branch
git unstage file.txt # вместо git reset HEAD file.txt
git lg               # красивый лог
```

---

## Git Hooks

Git hooks — это скрипты, автоматически выполняемые при определённых событиях.

**Расположение:** `.git/hooks/`

**Основные hooks:**
- `pre-commit` — перед созданием коммита
- `commit-msg` — проверка commit message
- `post-commit` — после создания коммита
- `pre-push` — перед push
- `post-merge` — после merge
- `pre-rebase` — перед rebase

**Пример pre-commit hook (проверка линтера):**
```bash
#!/bin/sh
npm run lint
```

**Активация:**
```bash
chmod +x .git/hooks/pre-commit
```

---

## Полезные комбинации

### Отменить последний commit, но оставить изменения
```bash
git reset --soft HEAD~1
```

### Изменить последний commit message
```bash
git commit --amend -m "Новое сообщение"
```

### Удалить последний commit полностью
```bash
git reset --hard HEAD~1
```

### Посмотреть, что изменится при pull
```bash
git fetch origin
git diff HEAD origin/main
```

### Создать ветку и переключиться на неё
```bash
git checkout -b new-feature
# или современный способ
git switch -c new-feature
```

### Удалить все локальные ветки, кроме main
```bash
git branch | grep -v "main" | xargs git branch -D
```

### Переименовать текущую ветку
```bash
git branch -m new-name
```

### Посмотреть изменения конкретного файла
```bash
git log -p file.txt
```

### Найти, в каком коммите был удалён файл
```bash
git log --all --full-history -- path/to/file
```

### Восстановить удалённый файл
```bash
git checkout <commit-hash>^ -- path/to/file
```

### Создать пустой коммит (для триггера CI/CD)
```bash
git commit --allow-empty -m "Trigger CI"
```

### Посмотреть все изменения автора
```bash
git log --author="Суxейль" --oneline
```

### Посмотреть статистику коммитов по авторам
```bash
git shortlog -sn
```

### Сжать последние N коммитов в один
```bash
git rebase -i HEAD~N
# В редакторе оставьте первый коммит как pick, остальные замените на squash
```

---

## Windows + Git Bash специфика

### Конвертация путей
```bash
# Windows путь
D:\Projects\MyApp

# Git Bash путь
/d/Projects/MyApp
```

### Права на выполнение (chmod)
```bash
# В Git Bash
chmod +x script.sh

# Альтернатива через Git
git update-index --chmod=+x script.sh
```

### Line endings (CRLF vs LF)
```bash
# Настройка для Windows (автоконвертация)
git config --global core.autocrlf true

# Для Linux/Mac
git config --global core.autocrlf input
```

### Решение проблем с кириллицей
```bash
# Корректное отображение русских имён файлов
git config --global core.quotepath false
```

---

## Заключение

Эта шпаргалка покрывает более 95% команд Git, с которыми вы столкнётесь в повседневной работе.

**Самые используемые команды (топ-10):**
1. `git status` — проверка состояния
2. `git add` — добавление изменений
3. `git commit` — создание коммита
4. `git push` — отправка на GitHub
5. `git pull` — получение изменений
6. `git clone` — клонирование репозитория
7. `git checkout` / `git switch` — переключение веток
8. `git branch` — управление ветками
9. `git merge` — слияние веток
10. `git log` — просмотр истории

✅ **Совет:** Добавьте эту шпаргалку в закладки и обращайтесь к ней по мере необходимости!
