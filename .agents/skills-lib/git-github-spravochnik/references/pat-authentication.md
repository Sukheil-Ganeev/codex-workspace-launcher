# Personal Access Token (PAT) Authentication

Полное руководство по использованию Personal Access Token для аутентификации на GitHub.

---

## Содержание

1. [Что такое Personal Access Token](#что-такое-personal-access-token)
2. [Почему больше нельзя использовать пароль](#почему-больше-нельзя-использовать-пароль)
3. [Создание Personal Access Token](#создание-personal-access-token)
4. [Использование PAT вместо пароля](#использование-pat-вместо-пароля)
5. [Сохранение credentials в Git](#сохранение-credentials-в-git)
6. [Обновление существующих credentials](#обновление-существующих-credentials)
7. [Security best practices](#security-best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Сравнение PAT vs SSH](#сравнение-pat-vs-ssh)

---

## Что такое Personal Access Token

**Personal Access Token (PAT)** — это альтернатива паролю для аутентификации в GitHub API и Git операциях.

**Формат:** `ghp_1234567890abcdefghijklmnopqrstuvwxyz`

**Преимущества:**
- ✅ Можно создать несколько токенов для разных проектов
- ✅ Можно ограничить права доступа (scopes)
- ✅ Можно отозвать без смены пароля
- ✅ Имеет срок действия (безопаснее)

**Недостатки:**
- ❌ Нужно хранить и обновлять
- ❌ Если потеряли, нужно создавать новый
- ❌ Сложнее настроить, чем SSH

---

## Почему больше нельзя использовать пароль

**С 13 августа 2021 года GitHub отключил аутентификацию по паролю** для Git операций.

**Если вы попытаетесь использовать пароль:**

```bash
$ git push
Username: suheil
Password: ********
remote: Support for password authentication was removed on August 13, 2021.
remote: Please use a personal access token instead.
fatal: Authentication failed for 'https://github.com/suheil/repo.git/'
```

❌ **Ошибка:** `Authentication failed`

**Решения:**
1. Использовать **Personal Access Token** (PAT)
2. Использовать **SSH** (рекомендуется)

---

## Создание Personal Access Token

### Классический токен (Classic Token)

**Шаг 1:** Откройте GitHub в браузере

**Шаг 2:** Нажмите на **аватар** (правый верхний угол) → **Settings**

**Шаг 3:** В боковом меню (внизу): **Developer settings**

**Шаг 4:** **Personal access tokens** → **Tokens (classic)**

**Шаг 5:** **Generate new token** → **Generate new token (classic)**

**Шаг 6:** Заполните форму:

| Поле | Значение |
|------|----------|
| **Note** | Описание токена (например: "Windows PC - Git operations") |
| **Expiration** | Срок действия (рекомендуется: 90 days) |
| **Select scopes** | Права доступа (см. ниже) |

**Рекомендуемые scopes для Git операций:**

✅ **Обязательные:**
- [x] `repo` — Полный доступ к репозиториям
  - [x] `repo:status`
  - [x] `repo_deployment`
  - [x] `public_repo`
  - [x] `repo:invite`
  - [x] `security_events`

✅ **Дополнительные (опционально):**
- [x] `workflow` — Доступ к GitHub Actions
- [x] `write:packages` — Публикация пакетов
- [x] `read:packages` — Чтение пакетов

**Шаг 7:** **Generate token**

**Шаг 8:** **ВАЖНО!** Скопируйте токен **СЕЙЧАС**

```
ghp_1234567890abcdefghijklmnopqrstuvwxyz1234567890
```

⚠️ **Внимание:** Токен показывается **ТОЛЬКО ОДИН РАЗ**! Если потеряете — придётся создавать новый.

**Сохраните токен:**
- В менеджере паролей (1Password, Bitwarden, LastPass)
- В безопасном текстовом файле (не в репозитории!)
- ❌ НЕ сохраняйте в открытом виде в коде!

---

### Fine-grained токен (новый тип)

**Fine-grained tokens** — более безопасные токены с детальной настройкой доступа.

**Создание:**

**Шаг 1-4:** Те же, что для классического токена

**Шаг 5:** **Personal access tokens** → **Fine-grained tokens**

**Шаг 6:** **Generate new token**

**Шаг 7:** Заполните форму:

| Поле | Значение |
|------|----------|
| **Token name** | "Git operations - Windows PC" |
| **Expiration** | 90 days |
| **Repository access** | All repositories / Only select repositories |

**Шаг 8:** **Repository permissions:**

| Разрешение | Уровень |
|------------|---------|
| **Contents** | Read and write |
| **Metadata** | Read-only (автоматически) |
| **Pull requests** | Read and write (если нужно) |
| **Workflows** | Read and write (для GitHub Actions) |

**Шаг 9:** **Generate token** и скопируйте

---

## Использование PAT вместо пароля

### При клонировании

```bash
git clone https://github.com/username/repo.git
Username: your-github-username
Password: ghp_1234567890abcdefghijklmnopqrstuvwxyz1234567890
```

⚠️ **Важно:** В поле "Password" вводите **токен**, а не пароль!

### При push

```bash
git push
Username: your-github-username
Password: ghp_1234567890abcdefghijklmnopqrstuvwxyz1234567890
```

### Встраивание токена в URL (не рекомендуется!)

```bash
git clone https://ghp_YOUR_TOKEN@github.com/username/repo.git
```

❌ **НЕ РЕКОМЕНДУЕТСЯ:** Токен будет виден в `.git/config` и в истории команд!

---

## Сохранение credentials в Git

### Windows: Git Credential Manager

**Git для Windows** включает **Git Credential Manager** (GCM), который автоматически сохраняет токены.

**Проверка, установлен ли GCM:**
```bash
git credential-manager --version
```

**Если установлен:**
```
Git Credential Manager version 2.x.x
```

**Настройка GCM:**
```bash
git config --global credential.helper manager
```

✅ **Теперь токен будет сохранён после первого ввода!**

**GCM хранит токены в:**
- **Windows Credential Manager** (Control Panel → Credential Manager → Windows Credentials)

**Просмотр в Windows:**
1. **Win + R** → `control`
2. **Credential Manager** → **Windows Credentials**
3. Найдите `git:https://github.com`

---

### Альтернатива: credential.helper store

**Сохранение токена в plaintext файл:**

```bash
git config --global credential.helper store
```

**При первом push введите токен:**
```bash
git push
Username: suheil
Password: ghp_YOUR_TOKEN
```

**Токен сохранится в файл:** `~/.git-credentials`

**Формат файла:**
```
https://suheil:ghp_YOUR_TOKEN@github.com
```

⚠️ **Внимание:** Токен хранится в **открытом виде**! Используйте только на личном компьютере.

**Проверка сохранённых credentials:**
```bash
cat ~/.git-credentials
```

---

### Альтернатива: credential.helper cache (Linux/Mac)

**Кэширование токена в памяти на 15 минут:**

```bash
git config --global credential.helper cache
```

**Кэширование на 1 час:**
```bash
git config --global credential.helper 'cache --timeout=3600'
```

⚠️ **Не работает на Windows!** Используйте `manager` или `store`.

---

## Обновление существующих credentials

### Если ошибка: Authentication failed

**Сценарий:** Вы ввели неправильный токен или токен истёк.

```bash
$ git push
remote: Invalid username or password.
fatal: Authentication failed for 'https://github.com/suheil/repo.git/'
```

**Решение:**

#### Windows (Git Credential Manager)

**Метод 1: Удалить через Windows Credential Manager**
1. **Win + R** → `control`
2. **Credential Manager** → **Windows Credentials**
3. Найдите `git:https://github.com`
4. **Remove** (Удалить)

**Метод 2: Через командную строку**
```bash
git credential-manager delete https://github.com
```

**Метод 3: Через Git**
```bash
git credential reject
protocol=https
host=github.com
```
Нажмите **Enter**, затем **Ctrl+Z** (Windows) или **Ctrl+D** (Git Bash)

**После удаления попробуйте снова:**
```bash
git push
Username: suheil
Password: ghp_NEW_TOKEN
```

---

#### Если используется credential.helper store

**Отредактируйте файл:**
```bash
nano ~/.git-credentials
```

**Или удалите строку с GitHub:**
```bash
sed -i '/github.com/d' ~/.git-credentials
```

**Попробуйте снова:**
```bash
git push
Username: suheil
Password: ghp_NEW_TOKEN
```

---

### Смена токена для конкретного репозитория

**Проверьте текущий remote:**
```bash
git remote -v
```

**Вывод:**
```
origin  https://github.com/suheil/repo.git (fetch)
origin  https://github.com/suheil/repo.git (push)
```

**Если токен встроен в URL:**
```
origin  https://ghp_OLD_TOKEN@github.com/suheil/repo.git (fetch)
```

**Обновите URL:**
```bash
git remote set-url origin https://github.com/suheil/repo.git
```

**Теперь при push введите новый токен.**

---

## Security best practices

### ✅ Хорошие практики

**1. Используйте Fine-grained tokens**
- Ограничивают доступ до конкретных репозиториев
- Более детальные права доступа

**2. Устанавливайте срок действия**
- Рекомендуется: 90 дней
- Не используйте "No expiration"

**3. Создавайте отдельные токены для разных целей**
- Токен для работы на компьютере
- Токен для CI/CD
- Токен для скриптов

**4. Минимизируйте scopes**
- Давайте только необходимые права
- Не используйте `admin:org` без крайней необходимости

**5. Храните токены безопасно**
- Используйте менеджер паролей
- Не коммитьте в репозиторий
- Не передавайте в открытом виде

**6. Регулярно обновляйте токены**
- При истечении создавайте новый
- Удаляйте старые токены

**7. Отзывайте компрометированные токены**
- Если токен попал в чужие руки — немедленно удалите
- Создайте новый токен

---

### ❌ Плохие практики

**1. НЕ коммитьте токены в репозиторий**
```bash
# .env
GITHUB_TOKEN=ghp_YOUR_TOKEN  # ❌ НИКОГДА!
```

**2. НЕ встраивайте токены в URL**
```bash
git clone https://ghp_TOKEN@github.com/user/repo.git  # ❌
```

**3. НЕ используйте "No expiration"**
- Токен без срока действия опасен
- Используйте минимум 30-90 дней

**4. НЕ давайте избыточные права**
```
Scopes: [x] admin:org  # ❌ Зачем?
        [x] delete_repo  # ❌ Опасно!
```

**5. НЕ делитесь токенами**
- Каждый пользователь должен иметь свой токен
- Не отправляйте токены по email/Telegram

---

### Проверка на утечку токенов

**GitHub автоматически сканирует публичные репозитории** и отзывает токены, случайно попавшие в код.

**Если токен найден:**
- GitHub отправит email: "A personal access token has been found"
- Токен будет немедленно отозван
- Вам нужно создать новый

**Как избежать:**
1. Добавьте в `.gitignore`:
```
.env
.env.local
credentials.json
config/secrets.yml
```

2. Используйте pre-commit hooks:
```bash
# .git/hooks/pre-commit
#!/bin/sh
if grep -r "ghp_" --exclude-dir=.git .; then
    echo "ERROR: GitHub token found in code!"
    exit 1
fi
```

3. Используйте инструменты:
   - [git-secrets](https://github.com/awslabs/git-secrets)
   - [truffleHog](https://github.com/trufflesecurity/truffleHog)

---

## Troubleshooting

### Ошибка: Authentication failed

**Симптомы:**
```bash
$ git push
remote: Invalid username or password.
fatal: Authentication failed
```

**Причины:**
1. Используете пароль вместо токена
2. Токен истёк
3. Токен неправильный
4. Недостаточно прав (scopes)

**Решение:**
1. Проверьте, что вводите **токен**, а не пароль
2. Проверьте срок действия токена на GitHub
3. Создайте новый токен
4. Удалите старые credentials (см. выше)

---

### Ошибка: Token doesn't have required scopes

**Симптомы:**
```bash
$ git push
remote: Write access to repository not granted.
fatal: unable to access 'https://github.com/user/repo.git/': The requested URL returned error: 403
```

**Причина:** Токен не имеет прав `repo`.

**Решение:**
1. Откройте GitHub → Settings → Developer settings → Tokens
2. Найдите токен
3. Нажмите **Edit**
4. Включите `repo` scope
5. **Regenerate token**
6. Обновите токен в Git credentials

---

### Ошибка: Token expired

**Симптомы:**
```bash
$ git push
remote: This token has expired.
fatal: Authentication failed
```

**Решение:**
1. Создайте новый токен (см. раздел "Создание")
2. Удалите старый токен из credentials
3. Введите новый токен при следующем push

---

### Проблема: Credential helper не работает

**Симптомы:** Git постоянно запрашивает токен.

**Проверка:**
```bash
git config --global credential.helper
```

**Если пусто или `cache`:**
```bash
git config --global credential.helper manager  # Windows
# или
git config --global credential.helper store  # Linux/Mac
```

---

### Проблема: Git использует старый токен

**Решение 1: Удалить из Windows Credential Manager**
```bash
git credential-manager delete https://github.com
```

**Решение 2: Удалить из store**
```bash
rm ~/.git-credentials
```

**Решение 3: Очистить кеш**
```bash
git credential-cache exit
```

---

## Сравнение PAT vs SSH

| Критерий | Personal Access Token | SSH |
|----------|------------------------|-----|
| **Простота настройки** | ⭐⭐⭐⭐ Легко | ⭐⭐⭐ Средне |
| **Безопасность** | ⭐⭐⭐ Хорошо | ⭐⭐⭐⭐⭐ Отлично |
| **Удобство использования** | ⭐⭐⭐ Нормально | ⭐⭐⭐⭐⭐ Отлично |
| **Срок действия** | ❌ Истекает | ✅ Бессрочно |
| **Поддержка прокси** | ✅ Да | ❌ Сложно |
| **CI/CD интеграция** | ✅ Легко | ⭐⭐⭐ Средне |
| **Множественные аккаунты** | ⭐⭐⭐ Средне | ⭐⭐⭐⭐⭐ Отлично |

**Вывод:**
- ✅ **SSH рекомендуется** для постоянной работы
- ✅ **PAT подходит** для временного доступа, CI/CD, скриптов

---

## Практический пример: Полная настройка

**Сценарий:** Вы клонировали репозиторий по HTTPS и получили ошибку Authentication failed.

**Решение пошагово:**

**Шаг 1: Создайте токен**
```
GitHub → Settings → Developer settings → Tokens (classic)
→ Generate new token → Выберите scopes: repo
→ Generate → Скопируйте токен
```

**Шаг 2: Настройте Git Credential Manager**
```bash
git config --global credential.helper manager
```

**Шаг 3: Попробуйте push**
```bash
git add .
git commit -m "Test commit"
git push
Username: suheil
Password: ghp_YOUR_TOKEN
```

**Шаг 4: Проверьте, что токен сохранён**
```bash
# Следующий push не должен запрашивать токен
echo "test" > test.txt
git add test.txt
git commit -m "Test 2"
git push  # Без запроса токена!
```

✅ **Готово!** Токен сохранён и работает.

---

## Заключение

Personal Access Token — это безопасный способ аутентификации для HTTPS клонирования и Git операций.

✅ **Рекомендации:**
- Используйте PAT для временного доступа
- Используйте SSH для постоянной работы
- Устанавливайте срок действия токенов
- Не коммитьте токены в репозиторий
- Регулярно обновляйте токены

⚠️ **Безопасность:**
- Храните токены в менеджере паролей
- Не делитесь токенами
- Отзывайте компрометированные токены
- Используйте минимальные scopes

🎯 **Для туристического бизнеса:**
PAT полезен для автоматизации (CI/CD, скрипты, боты), но для ежедневной работы рекомендуется SSH.
