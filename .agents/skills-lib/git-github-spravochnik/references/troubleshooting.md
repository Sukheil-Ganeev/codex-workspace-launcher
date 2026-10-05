# Troubleshooting - Решение проблем Git и GitHub

Справочник по типичным ошибкам Git/GitHub с пошаговыми решениями.

---

## Проблемы с Authentication

### ❌ Ошибка: Authentication failed / Support for password authentication was removed

**Симптомы:**
```bash
remote: Support for password authentication was removed on August 13, 2021.
remote: Please use a personal access token instead.
fatal: Authentication failed for 'https://github.com/user/repo.git/'
```

**Причина:**
GitHub больше не принимает обычные пароли для HTTPS операций. Необходим Personal Access Token (PAT).

**Решение:**

1. **Создать Personal Access Token на GitHub:**
   - Перейти на https://github.com/settings/tokens
   - Нажать "Generate new token" → "Generate new token (classic)"
   - Дать имя токену: "Git CLI Access"
   - Выбрать срок действия (рекомендуется 90 дней или custom)
   - Отметить scopes:
     - ✅ `repo` (полный доступ к репозиториям)
     - ✅ `workflow` (если используете GitHub Actions)
   - Нажать "Generate token"
   - ⚠️ **СКОПИРОВАТЬ ТОКЕН СРАЗУ!** Повторно его не покажут

2. **Использовать токен вместо пароля:**
   ```bash
   # При следующем git push/pull/clone
   Username: ваш-username
   Password: ghp_ваш_токен_здесь
   ```

3. **Сохранить credentials чтобы не вводить каждый раз:**
   ```bash
   # Windows (использовать Credential Manager)
   git config --global credential.helper manager-core

   # Или сохранить в файл (менее безопасно)
   git config --global credential.helper store

   # После этого выполните любую операцию
   git push
   # Введите username и PAT - они сохранятся автоматически
   ```

4. **Альтернатива - использовать SSH ключи:**
   ```bash
   # Изменить remote URL с HTTPS на SSH
   git remote set-url origin git@github.com:user/repo.git

   # Теперь push/pull будут работать через SSH (без PAT)
   ```

✅ **Подробнее:** См. `pat-authentication.md` для детальной инструкции.

---

### ❌ Ошибка: Permission denied (publickey)

**Симптомы:**
```bash
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

**Причина:**
GitHub не может аутентифицировать вас по SSH ключу. Либо ключ не добавлен на GitHub, либо SSH agent не запущен.

**Решение:**

1. **Проверить существующие SSH ключи:**
   ```bash
   ls -la ~/.ssh
   # Ищите файлы: id_rsa, id_ed25519, id_rsa.pub, id_ed25519.pub
   ```

2. **Если ключей нет - создать новый:**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # Нажмите Enter для дефолтного пути
   # Можете установить passphrase или оставить пустым
   ```

3. **Запустить SSH agent (Windows Git Bash):**
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

4. **Добавить публичный ключ на GitHub:**
   ```bash
   # Скопировать публичный ключ
   cat ~/.ssh/id_ed25519.pub
   # Скопируйте весь вывод (начинается с ssh-ed25519...)
   ```

   - Перейти на https://github.com/settings/keys
   - Нажать "New SSH key"
   - Title: "My Windows PC"
   - Key: вставить скопированный ключ
   - Нажать "Add SSH key"

5. **Проверить подключение:**
   ```bash
   ssh -T git@github.com
   # Должно вывести: Hi username! You've successfully authenticated...
   ```

✅ **Подробнее:** См. `ssh-setup-windows.md` для детальной инструкции.

---

### ❌ Ошибка: Could not resolve host: github.com

**Симптомы:**
```bash
fatal: unable to access 'https://github.com/user/repo.git/':
Could not resolve host: github.com
```

**Причина:**
Проблемы с интернет-соединением или DNS.

**Решение:**

1. **Проверить интернет:**
   ```bash
   ping github.com
   # Должен показать ответы от сервера
   ```

2. **Попробовать другой DNS:**
   ```bash
   # В Windows: Настройки → Сеть → Изменить параметры адаптера
   # → Свойства → IPv4 → Использовать DNS:
   # 8.8.8.8 (Google DNS)
   # 1.1.1.1 (Cloudflare DNS)
   ```

3. **Проверить proxy настройки:**
   ```bash
   git config --global --get http.proxy
   git config --global --get https.proxy

   # Если не используете proxy, удалить:
   git config --global --unset http.proxy
   git config --global --unset https.proxy
   ```

4. **Временно использовать SSH вместо HTTPS:**
   ```bash
   git remote set-url origin git@github.com:user/repo.git
   ```

---

## Проблемы с Merge

### ❌ Ошибка: CONFLICT (content) - Merge conflict

**Симптомы:**
```bash
Auto-merging file.txt
CONFLICT (content): Merge conflict in file.txt
Automatic merge failed; fix conflicts and then commit the result.
```

**Причина:**
Одни и те же строки в файле были изменены по-разному в двух ветках.

**Решение:**

1. **Посмотреть какие файлы в конфликте:**
   ```bash
   git status
   # Файлы с конфликтами помечены как "both modified"
   ```

2. **Открыть файл и найти маркеры конфликта:**
   ```
   <<<<<<< HEAD (текущая ветка)
   console.log("Hello from main");
   =======
   console.log("Hello from feature");
   >>>>>>> feature-branch
   ```

3. **Разрешить конфликт вручную:**
   - Удалить маркеры `<<<<<<<`, `=======`, `>>>>>>>`
   - Оставить нужный код (или объединить оба варианта)

   Пример результата:
   ```javascript
   console.log("Hello from feature");
   ```

4. **Добавить разрешённый файл и завершить merge:**
   ```bash
   git add file.txt
   git commit -m "Resolve merge conflict in file.txt"
   ```

5. **Альтернатива - отменить merge:**
   ```bash
   git merge --abort
   ```

💡 **Совет:** Используйте merge tool для визуального разрешения конфликтов:
```bash
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'
git mergetool
```

---

### ❌ Ошибка: refusing to merge unrelated histories

**Симптомы:**
```bash
fatal: refusing to merge unrelated histories
```

**Причина:**
Пытаетесь слить две ветки/репозитория у которых нет общих коммитов (разные корни истории).

**Решение:**

1. **Если это действительно нужно - форсировать merge:**
   ```bash
   git pull origin main --allow-unrelated-histories
   ```

2. **Разрешить возможные конфликты:**
   ```bash
   # После merge могут быть конфликты
   git status
   # Разрешите их и завершите:
   git add .
   git commit -m "Merge unrelated histories"
   ```

**Когда возникает:**
- Клонировали пустой репозиторий на GitHub, создали локальный репозиторий отдельно
- Пытаетесь слить два независимых проекта

---

## Проблемы с Push/Pull

### ❌ Ошибка: Updates were rejected because the tip of your current branch is behind

**Симптомы:**
```bash
! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/user/repo.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. Integrate the remote changes (e.g. 'git pull ...')
hint: before pushing again.
```

**Причина:**
На удалённом репозитории есть коммиты, которых нет в вашей локальной ветке.

**Решение:**

1. **Сначала получить изменения с remote:**
   ```bash
   git pull origin main
   ```

2. **Если есть конфликты - разрешить их:**
   ```bash
   git status
   # Разрешите конфликты
   git add .
   git commit -m "Merge remote changes"
   ```

3. **Теперь можно push:**
   ```bash
   git push origin main
   ```

4. **Альтернатива - использовать rebase:**
   ```bash
   git pull --rebase origin main
   # Разрешите конфликты если есть
   git rebase --continue
   git push origin main
   ```

⚠️ **Если уверены что хотите перезаписать remote (опасно!):**
```bash
git push --force-with-lease origin main
```
❌ **Никогда не делайте `--force` в ветки main/master или общие ветки!**

---

### ❌ Ошибка: The current branch has no upstream branch

**Симптомы:**
```bash
fatal: The current branch feature-branch has no upstream branch.
To push the current branch and set the remote as upstream, use

    git push --set-upstream origin feature-branch
```

**Причина:**
Ветка существует только локально, Git не знает куда её push'ить на remote.

**Решение:**

```bash
# Вариант 1 (рекомендуется)
git push -u origin feature-branch

# Вариант 2 (более длинная форма)
git push --set-upstream origin feature-branch
```

После этого можно использовать просто `git push` без указания remote и ветки.

---

### ❌ Ошибка: src refspec main does not match any

**Симптомы:**
```bash
error: src refspec main does not match any
error: failed to push some refs to 'https://github.com/user/repo.git'
```

**Причина:**
Пытаетесь push'нуть ветку main, но она не существует локально или в ней нет коммитов.

**Решение:**

1. **Проверить какие ветки есть:**
   ```bash
   git branch -a
   ```

2. **Если используется ветка master вместо main:**
   ```bash
   git push -u origin master
   ```

3. **Если вообще нет коммитов:**
   ```bash
   # Создайте первый коммит
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

4. **Переименовать ветку master в main (если нужно):**
   ```bash
   git branch -m master main
   git push -u origin main
   ```

---

## Проблемы с Repository

### ❌ Ошибка: fatal: not a git repository

**Симптомы:**
```bash
fatal: not a git repository (or any of the parent directories): .git
```

**Причина:**
Выполняете Git команды не в директории с Git репозиторием.

**Решение:**

1. **Проверить текущую директорию:**
   ```bash
   pwd  # В Git Bash
   # или
   cd   # в CMD
   ```

2. **Перейти в нужную директорию:**
   ```bash
   cd /d/Projects/my-repo
   ```

3. **Если репозиторий не инициализирован:**
   ```bash
   git init
   ```

4. **Или клонировать существующий:**
   ```bash
   git clone https://github.com/user/repo.git
   cd repo
   ```

---

### ❌ Ошибка: fatal: remote origin already exists

**Симптомы:**
```bash
fatal: remote origin already exists.
```

**Причина:**
Пытаетесь добавить remote с именем origin, но он уже существует.

**Решение:**

1. **Посмотреть существующие remotes:**
   ```bash
   git remote -v
   ```

2. **Удалить существующий и добавить новый:**
   ```bash
   git remote remove origin
   git remote add origin https://github.com/user/new-repo.git
   ```

3. **Или изменить URL существующего:**
   ```bash
   git remote set-url origin https://github.com/user/new-repo.git
   ```

4. **Или добавить с другим именем:**
   ```bash
   git remote add upstream https://github.com/user/repo.git
   ```

---

### ❌ Ошибка: fatal: repository not found

**Симптомы:**
```bash
remote: Repository not found.
fatal: repository 'https://github.com/user/repo.git/' not found
```

**Причина:**
1. Репозиторий не существует
2. У вас нет доступа к приватному репозиторию
3. Опечатка в URL

**Решение:**

1. **Проверить URL репозитория:**
   ```bash
   git remote -v
   # Убедитесь что URL правильный
   ```

2. **Проверить на GitHub существует ли репозиторий:**
   - Откройте URL в браузере
   - Убедитесь что вы авторизованы и имеете доступ

3. **Исправить URL если есть опечатка:**
   ```bash
   git remote set-url origin https://github.com/correct-user/correct-repo.git
   ```

4. **Проверить authentication:**
   ```bash
   # Для HTTPS - нужен PAT
   # Для SSH - нужен SSH ключ
   ssh -T git@github.com
   ```

---

## Проблемы с Branches

### ❌ Ошибка: cannot delete branch you are currently on

**Симптомы:**
```bash
error: Cannot delete branch 'feature' checked out at '/path/to/repo'
```

**Причина:**
Пытаетесь удалить ветку на которой сейчас находитесь.

**Решение:**

```bash
# Переключиться на другую ветку
git checkout main

# Теперь можно удалить
git branch -d feature
```

---

### ❌ Ошибка: error: The branch is not fully merged

**Симптомы:**
```bash
error: The branch 'feature' is not fully merged.
If you are sure you want to delete it, run 'git branch -D feature'.
```

**Причина:**
Ветка содержит коммиты которые не слиты в текущую ветку. Git защищает от случайной потери данных.

**Решение:**

1. **Если хотите сохранить изменения - сначала слить:**
   ```bash
   git checkout main
   git merge feature
   git branch -d feature
   ```

2. **Если уверены что хотите удалить без слияния:**
   ```bash
   git branch -D feature
   ```

3. **Проверить что будет потеряно:**
   ```bash
   git log main..feature --oneline
   # Покажет коммиты которые будут потеряны
   ```

---

### ❌ Проблема: Detached HEAD state

**Симптомы:**
```bash
Note: switching to 'abc123'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.
```

**Причина:**
Переключились на конкретный коммит (не на ветку). HEAD указывает на коммит, а не на ветку.

**Решение:**

1. **Если просто смотрели код - вернуться на ветку:**
   ```bash
   git checkout main
   # или
   git switch main
   ```

2. **Если сделали изменения и хотите их сохранить:**
   ```bash
   # Создать ветку из текущего состояния
   git checkout -b new-feature
   # или
   git switch -c new-feature
   ```

3. **Если сделали коммиты в detached state:**
   ```bash
   # Сохранить hash последнего коммита
   git log -1
   # Вернуться на ветку
   git checkout main
   # Cherry-pick нужные коммиты
   git cherry-pick <commit-hash>
   ```

---

## Проблемы с Staging

### ❌ Ошибка: Your local changes would be overwritten by checkout

**Симптомы:**
```bash
error: Your local changes to the following files would be overwritten by checkout:
        file.txt
Please commit your changes or stash them before you switch branches.
Aborting
```

**Причина:**
Пытаетесь переключить ветку, но есть несохранённые изменения которые конфликтуют с целевой веткой.

**Решение:**

1. **Сохранить изменения (commit):**
   ```bash
   git add .
   git commit -m "WIP: save current work"
   git checkout other-branch
   ```

2. **Временно спрятать изменения (stash):**
   ```bash
   git stash
   git checkout other-branch
   # Позже вернуть:
   git checkout -
   git stash pop
   ```

3. **Отменить изменения (если не нужны):**
   ```bash
   git restore file.txt
   # или отменить все
   git restore .
   git checkout other-branch
   ```

---

### ❌ Проблема: Случайно добавили файл в staging

**Решение:**

```bash
# Убрать конкретный файл
git restore --staged file.txt

# Убрать все файлы из staging
git restore --staged .

# Старый способ (тоже работает)
git reset HEAD file.txt
git reset HEAD .
```

---

### ❌ Проблема: Случайно закоммитили файл который не должен был попасть в Git

**Решение:**

1. **Если это последний коммит (не push'нут):**
   ```bash
   # Убрать файл из коммита
   git reset HEAD~1
   # Добавить в .gitignore
   echo "secret.txt" >> .gitignore
   # Закоммитить остальное
   git add .
   git commit -m "Add features (without secret.txt)"
   ```

2. **Если коммит уже push'нут:**
   ```bash
   # Удалить файл из tracking, но оставить локально
   git rm --cached secret.txt
   # Добавить в .gitignore
   echo "secret.txt" >> .gitignore
   git add .gitignore
   git commit -m "Remove secret.txt from tracking"
   git push
   ```

⚠️ **Важно:** Файл всё равно остался в истории! Если это пароли/ключи - смените их и используйте `git filter-repo` для полного удаления из истории.

---

## Проблемы с .gitignore

### ❌ Проблема: .gitignore не работает, файлы всё равно отслеживаются

**Причина:**
Файлы уже добавлены в Git tracking до создания .gitignore.

**Решение:**

1. **Убрать файлы из tracking:**
   ```bash
   # Конкретный файл
   git rm --cached file.txt

   # Конкретная папка
   git rm --cached -r node_modules/

   # Все игнорируемые файлы
   git rm -r --cached .
   git add .
   ```

2. **Создать/обновить .gitignore:**
   ```bash
   echo "node_modules/" >> .gitignore
   echo "*.log" >> .gitignore
   ```

3. **Закоммитить изменения:**
   ```bash
   git add .gitignore
   git commit -m "Update .gitignore and remove tracked files"
   git push
   ```

---

## Проблемы с Commit

### ❌ Проблема: Хочу изменить последний commit message

**Решение:**

1. **Если коммит не push'нут:**
   ```bash
   git commit --amend -m "New correct message"
   ```

2. **Если коммит уже push'нут (осторожно!):**
   ```bash
   git commit --amend -m "New correct message"
   git push --force-with-lease
   ```

⚠️ **Важно:** Force push опасен для shared веток! Используйте только для своих feature веток.

---

### ❌ Проблема: Хочу отменить последний коммит

**Решение:**

1. **Отменить коммит, оставить изменения в staging:**
   ```bash
   git reset --soft HEAD~1
   ```

2. **Отменить коммит, оставить изменения unstaged:**
   ```bash
   git reset --mixed HEAD~1
   # или просто
   git reset HEAD~1
   ```

3. **Полностью удалить коммит и изменения:**
   ```bash
   git reset --hard HEAD~1
   ```

4. **Создать новый коммит отменяющий предыдущий (для public веток):**
   ```bash
   git revert HEAD
   ```

---

### ❌ Ошибка: gpg failed to sign the data

**Симптомы:**
```bash
error: gpg failed to sign the data
fatal: failed to write commit object
```

**Причина:**
Включена подпись коммитов GPG ключом, но ключ не настроен или GPG не работает.

**Решение:**

1. **Отключить GPG подпись:**
   ```bash
   git config --global commit.gpgsign false
   ```

2. **Или настроить GPG ключ (если нужна подпись):**
   ```bash
   # Создать GPG ключ
   gpg --full-generate-key

   # Получить ID ключа
   gpg --list-secret-keys --keyid-format=long

   # Настроить Git
   git config --global user.signingkey YOUR_KEY_ID
   git config --global commit.gpgsign true
   ```

---

## Проблемы с Line Endings (Windows)

### ❌ Проблема: warning: LF will be replaced by CRLF

**Симптомы:**
```bash
warning: LF will be replaced by CRLF in file.txt.
The file will have its original line endings in your working directory
```

**Причина:**
Windows использует CRLF (`\r\n`) для переводов строк, Linux/Mac используют LF (`\n`). Git пытается автоматически конвертировать.

**Решение:**

1. **Настроить автоконвертацию для Windows:**
   ```bash
   git config --global core.autocrlf true
   ```

2. **Для Linux/Mac:**
   ```bash
   git config --global core.autocrlf input
   ```

3. **Отключить warning (если он раздражает):**
   ```bash
   git config --global core.safecrlf false
   ```

4. **Использовать .gitattributes для контроля:**
   ```
   # .gitattributes
   * text=auto
   *.js text eol=lf
   *.bat text eol=crlf
   ```

---

## Проблемы с Performance

### ❌ Проблема: Git очень медленно работает

**Решение:**

1. **Запустить сборку мусора:**
   ```bash
   git gc --aggressive --prune=now
   ```

2. **Использовать shallow clone для больших репозиториев:**
   ```bash
   git clone --depth 1 https://github.com/user/large-repo.git
   ```

3. **Отключить автоматический gc:**
   ```bash
   git config --global gc.auto 0
   ```

4. **Использовать .gitignore для node_modules и т.п.:**
   ```bash
   echo "node_modules/" >> .gitignore
   ```

---

### ❌ Проблема: git status зависает или очень медленный

**Причина:**
Очень много файлов в рабочей директории (особенно node_modules).

**Решение:**

1. **Добавить в .gitignore:**
   ```bash
   echo "node_modules/" >> .gitignore
   git rm -r --cached node_modules/
   ```

2. **Использовать краткий формат:**
   ```bash
   git status -s
   ```

3. **Отключить отслеживание untracked файлов:**
   ```bash
   git status -uno
   ```

⚠️ **НИКОГДА НЕ ИСПОЛЬЗУЙТЕ:** `git status -uall` на больших репозиториях - может вызвать проблемы с памятью!

---

## Проблемы с Submodules

### ❌ Ошибка: fatal: no submodule mapping found

**Причина:**
Клонировали репозиторий с submodules, но они не инициализированы.

**Решение:**

```bash
# Инициализировать и обновить submodules
git submodule update --init --recursive
```

---

## Проблемы с Git Bash (Windows)

### ❌ Проблема: Русские имена файлов отображаются как \321\204...

**Решение:**

```bash
git config --global core.quotepath false
```

---

### ❌ Проблема: Пути Windows не работают в Git Bash

**Причина:**
Git Bash использует Unix-стиль путей.

**Решение:**

```bash
# Windows путь
D:\Projects\MyApp

# Git Bash путь
/d/Projects/MyApp

# Конвертация
cd /d/Projects/MyApp
```

---

## Экстренное восстановление

### 💣 Проблема: Случайно удалил важный коммит

**Решение:**

1. **Использовать reflog для поиска:**
   ```bash
   git reflog
   # Найдите hash потерянного коммита
   ```

2. **Восстановить коммит:**
   ```bash
   git checkout <commit-hash>
   git checkout -b recovery-branch
   ```

3. **Или cherry-pick в текущую ветку:**
   ```bash
   git cherry-pick <commit-hash>
   ```

💡 **Важно:** reflog хранит историю 90 дней по умолчанию. Почти всегда можно восстановить!

---

### 💣 Проблема: Случайно сделал git reset --hard и потерял изменения

**Решение:**

1. **Проверить reflog:**
   ```bash
   git reflog
   ```

2. **Вернуться к состоянию до reset:**
   ```bash
   git reset --hard HEAD@{1}
   # или конкретный hash
   git reset --hard <commit-hash>
   ```

---

### 💣 Проблема: Нужно полностью откатить репозиторий к предыдущему состоянию

**Решение:**

1. **Узнать hash нужного коммита:**
   ```bash
   git log --oneline
   ```

2. **Откатиться:**
   ```bash
   git reset --hard <commit-hash>
   ```

3. **Force push (если уже push'нуто):**
   ```bash
   git push --force-with-lease origin main
   ```

⚠️ **Внимание:** Это опасная операция! Используйте только если уверены.

---

## Полезные команды для диагностики

```bash
# Проверить конфигурацию
git config --list

# Проверить remote
git remote -v

# Проверить tracking ветки
git branch -vv

# Проверить состояние
git status

# История действий
git reflog

# Подробная информация о remote
git remote show origin

# Проверить SSH подключение
ssh -T git@github.com

# Проверить версию Git
git --version

# Очистка и оптимизация
git gc --aggressive --prune=now
```

---

## Чек-лист: что делать когда всё сломалось

1. ✅ `git status` - понять текущее состояние
2. ✅ `git log --oneline -5` - посмотреть последние коммиты
3. ✅ `git reflog` - если потеряли коммиты
4. ✅ `git remote -v` - проверить remote URL
5. ✅ Проверить authentication (PAT или SSH)
6. ✅ `git fetch origin` - обновить информацию о remote
7. ✅ Почитать error message внимательно - Git обычно подсказывает решение
8. ✅ Искать в этом файле по ключевым словам ошибки

---

## Когда обращаться за помощью

Если после всех попыток проблема не решается:

1. Скопируйте **полный текст ошибки**
2. Скопируйте команду которую вводили
3. Выполните `git status` и скопируйте вывод
4. Выполните `git remote -v` и скопируйте вывод
5. Выполните `git log --oneline -3` и скопируйте вывод

С этой информацией можно искать решение в Google или просить помощи.

---

✅ **Помните:** Почти всегда можно восстановить данные благодаря `git reflog` и внутреннему устройству Git!
