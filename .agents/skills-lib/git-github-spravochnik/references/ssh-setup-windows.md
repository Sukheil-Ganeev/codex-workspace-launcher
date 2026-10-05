# SSH Setup для Windows

Полное руководство по настройке SSH ключей для работы с GitHub на Windows.

---

## Содержание

1. [Что такое SSH](#что-такое-ssh)
2. [Преимущества SSH](#преимущества-ssh)
3. [Проверка существующих SSH ключей](#проверка-существующих-ssh-ключей)
4. [Генерация нового SSH ключа](#генерация-нового-ssh-ключа)
5. [Добавление ключа в ssh-agent](#добавление-ключа-в-ssh-agent)
6. [Добавление SSH ключа на GitHub](#добавление-ssh-ключа-на-github)
7. [Тестирование подключения](#тестирование-подключения)
8. [Использование SSH с Git](#использование-ssh-с-git)
9. [Troubleshooting](#troubleshooting)
10. [Работа с несколькими аккаунтами](#работа-с-несколькими-аккаунтами)

---

## Что такое SSH

**SSH (Secure Shell)** — криптографический протокол для безопасного подключения к удалённым серверам.

**SSH ключ** состоит из двух частей:
- **Приватный ключ** (`id_ed25519`) — хранится на вашем компьютере, НИКОГДА не передаётся
- **Публичный ключ** (`id_ed25519.pub`) — добавляется на GitHub

**Аналогия:** Публичный ключ — это замок, приватный ключ — это ключ от замка.

---

## Преимущества SSH

✅ **Безопасность:** Не нужно вводить пароль при каждом push/pull

✅ **Удобство:** Один раз настроил — работает всегда

✅ **Обязательность:** GitHub отключил аутентификацию по паролю (с августа 2021)

✅ **Поддержка множественных аккаунтов:** Можно настроить разные ключи для разных аккаунтов

---

## Проверка существующих SSH ключей

**Шаг 1:** Откройте **Git Bash** (не PowerShell, не CMD!)

**Шаг 2:** Проверьте наличие ключей:

```bash
ls -al ~/.ssh
```

**Что вы можете увидеть:**

✅ **Если ключи уже есть:**
```
id_ed25519
id_ed25519.pub
id_rsa
id_rsa.pub
```

❌ **Если ключей нет:**
```
ls: cannot access '/c/Users/londo/.ssh': No such file or directory
```

**Типы ключей:**
- `id_ed25519` / `id_ed25519.pub` — современный тип (рекомендуется)
- `id_rsa` / `id_rsa.pub` — старый тип (всё ещё работает)

⚠️ **Если у вас уже есть ключи:** Можете использовать существующие или создать новые.

---

## Генерация нового SSH ключа

### Рекомендуемый метод (ED25519)

**Откройте Git Bash** и выполните:

```bash
ssh-keygen -t ed25519 -C "suheil@example.com"
```

**Замените** `suheil@example.com` на свой **реальный email GitHub**.

**Что произойдёт:**

1. **Вопрос о расположении файла:**
```
Enter file in which to save the key (/c/Users/londo/.ssh/id_ed25519):
```

✅ **Рекомендация:** Нажмите **Enter** (использовать путь по умолчанию)

2. **Вопрос о passphrase (пароле для ключа):**
```
Enter passphrase (empty for no passphrase):
```

✅ **Рекомендация для личных компьютеров:** Нажмите **Enter** (без пароля)
⚠️ **Для рабочих компьютеров:** Введите надёжный пароль

3. **Подтверждение passphrase:**
```
Enter same passphrase again:
```

Нажмите **Enter** снова (или повторите пароль).

**Результат:**
```
Your identification has been saved in /c/Users/londo/.ssh/id_ed25519
Your public key has been saved in /c/Users/londo/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:AbCdEfGhIjKlMnOpQrStUvWxYz1234567890 suheil@example.com
```

✅ **Готово!** Ключ создан.

### Альтернативный метод (RSA)

Если ED25519 не поддерживается (очень старые системы):

```bash
ssh-keygen -t rsa -b 4096 -C "suheil@example.com"
```

⚠️ **Не рекомендуется:** ED25519 быстрее и безопаснее.

---

## Добавление ключа в ssh-agent

**ssh-agent** — фоновая программа, управляющая вашими SSH ключами.

### Шаг 1: Запуск ssh-agent

**Откройте Git Bash** и выполните:

```bash
eval "$(ssh-agent -s)"
```

**Ожидаемый вывод:**
```
Agent pid 1234
```

✅ **Это означает, что ssh-agent запущен.**

### Шаг 2: Добавление ключа в ssh-agent

```bash
ssh-add ~/.ssh/id_ed25519
```

**Ожидаемый вывод:**
```
Identity added: /c/Users/londo/.ssh/id_ed25519 (suheil@example.com)
```

✅ **Готово!** Ключ добавлен в агент.

### Проверка добавленных ключей

```bash
ssh-add -l
```

**Вывод:**
```
256 SHA256:AbCdEfGhIjKlMnOpQrStUvWxYz1234567890 suheil@example.com (ED25519)
```

---

## Windows специфика: Автозапуск ssh-agent

**Проблема:** В Windows ssh-agent не запускается автоматически при открытии Git Bash.

**Решение 1: Использование OpenSSH в Windows**

Windows 10/11 имеет встроенный OpenSSH сервис:

1. **Откройте PowerShell как Администратор**

2. **Включите OpenSSH Authentication Agent:**
```powershell
Get-Service -Name ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
```

3. **Добавьте ключ:**
```powershell
ssh-add C:\Users\londo\.ssh\id_ed25519
```

**Решение 2: Автоматический запуск в Git Bash**

Добавьте в `~/.bashrc` или `~/.bash_profile`:

```bash
# Автозапуск ssh-agent
env=~/.ssh/agent.env

agent_load_env () { test -f "$env" && . "$env" >| /dev/null ; }

agent_start () {
    (umask 077; ssh-agent >| "$env")
    . "$env" >| /dev/null ; }

agent_load_env

# Проверка, запущен ли агент
agent_run_state=$(ssh-add -l >| /dev/null 2>&1; echo $?)
if [ ! "$SSH_AUTH_SOCK" ] || [ $agent_run_state = 2 ]; then
    agent_start
    ssh-add ~/.ssh/id_ed25519
elif [ "$SSH_AUTH_SOCK" ] && [ $agent_run_state = 1 ]; then
    ssh-add ~/.ssh/id_ed25519
fi

unset env
```

**Применить изменения:**
```bash
source ~/.bashrc
```

✅ **Теперь ssh-agent будет запускаться автоматически!**

---

## Добавление SSH ключа на GitHub

### Шаг 1: Скопировать публичный ключ

**В Git Bash:**

```bash
cat ~/.ssh/id_ed25519.pub
```

**Вывод будет выглядеть так:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAbCdEfGhIjKlMnOpQrStUvWxYz1234567890 suheil@example.com
```

**Скопируйте весь текст** (от `ssh-ed25519` до конца).

**Альтернативный способ (копирование в буфер обмена):**
```bash
clip < ~/.ssh/id_ed25519.pub
```

✅ **Ключ скопирован в буфер обмена!**

### Шаг 2: Добавить ключ на GitHub

1. **Откройте GitHub** в браузере

2. **Нажмите на аватар** (правый верхний угол) → **Settings**

3. **Боковое меню:** **SSH and GPG keys**

4. **Нажмите:** **New SSH key**

5. **Заполните форму:**
   - **Title:** `Windows PC` (или любое понятное название)
   - **Key type:** `Authentication Key`
   - **Key:** Вставьте скопированный публичный ключ

6. **Нажмите:** **Add SSH key**

7. **Подтвердите паролем GitHub** (если требуется)

✅ **Готово!** SSH ключ добавлен на GitHub.

---

## Тестирование подключения

**В Git Bash:**

```bash
ssh -T git@github.com
```

**При первом подключении вы увидите предупреждение:**
```
The authenticity of host 'github.com (IP_ADDRESS)' can't be established.
ED25519 key fingerprint is SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

**Введите:** `yes`

**Ожидаемый успешный вывод:**
```
Hi Suheil! You've successfully authenticated, but GitHub does not provide shell access.
```

✅ **Успех!** SSH работает правильно.

❌ **Если ошибка:**
```
Permission denied (publickey).
```

Смотрите раздел [Troubleshooting](#troubleshooting).

---

## Использование SSH с Git

### Клонирование репозитория по SSH

**Вместо HTTPS:**
```bash
git clone https://github.com/username/repo.git
```

**Используйте SSH:**
```bash
git clone git@github.com:username/repo.git
```

### Изменение существующего репозитория на SSH

**Проверьте текущий remote:**
```bash
git remote -v
```

**Вывод (HTTPS):**
```
origin  https://github.com/username/repo.git (fetch)
origin  https://github.com/username/repo.git (push)
```

**Смените на SSH:**
```bash
git remote set-url origin git@github.com:username/repo.git
```

**Проверьте снова:**
```bash
git remote -v
```

**Вывод (SSH):**
```
origin  git@github.com:username/repo.git (fetch)
origin  git@github.com:username/repo.git (push)
```

✅ **Готово!** Теперь используется SSH.

### Автоматическое использование SSH

**Настройка Git для автоматической конвертации HTTPS → SSH:**

```bash
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

✅ **Теперь все HTTPS ссылки будут автоматически конвертироваться в SSH!**

---

## Troubleshooting

### Ошибка: Permission denied (publickey)

**Симптомы:**
```bash
$ ssh -T git@github.com
Permission denied (publickey).
```

**Причины:**
1. SSH ключ не добавлен на GitHub
2. ssh-agent не запущен
3. Ключ не добавлен в ssh-agent
4. Неправильные права доступа к ключу

**Решение 1: Проверьте ssh-agent**
```bash
ssh-add -l
```

Если выводит `Could not open a connection to your authentication agent`, запустите:
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

**Решение 2: Проверьте права доступа**
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

**Решение 3: Проверьте, добавлен ли ключ на GitHub**

Скопируйте публичный ключ:
```bash
cat ~/.ssh/id_ed25519.pub
```

Проверьте на GitHub: Settings → SSH and GPG keys

**Решение 4: Verbose вывод для диагностики**
```bash
ssh -vT git@github.com
```

Ищите строки:
```
debug1: Offering public key: /c/Users/londo/.ssh/id_ed25519 ED25519
debug1: Server accepts key: /c/Users/londo/.ssh/id_ed25519 ED25519
```

### Ошибка: Could not open a connection to your authentication agent

**Причина:** ssh-agent не запущен.

**Решение:**
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### Ошибка: Bad owner or permissions on ~/.ssh/config

**Причина:** Неправильные права доступа.

**Решение:**
```bash
chmod 600 ~/.ssh/config
```

### Проблема: ssh-agent не запускается автоматически

**Решение:** Используйте автозапуск (см. раздел [Windows специфика](#windows-специфика-автозапуск-ssh-agent))

### Ошибка: Host key verification failed

**Причина:** Fingerprint GitHub изменился или ещё не добавлен.

**Решение:**
```bash
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

### Проблема: Несколько SSH ключей

**Симптомы:** Git использует неправильный ключ.

**Решение:** Создайте файл `~/.ssh/config`:
```bash
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

---

## Работа с несколькими аккаунтами

### Сценарий: Личный и рабочий аккаунт GitHub

**Шаг 1: Создайте отдельные SSH ключи**

**Личный ключ:**
```bash
ssh-keygen -t ed25519 -C "personal@example.com" -f ~/.ssh/id_ed25519_personal
```

**Рабочий ключ:**
```bash
ssh-keygen -t ed25519 -C "work@company.com" -f ~/.ssh/id_ed25519_work
```

**Шаг 2: Добавьте ключи в ssh-agent**
```bash
ssh-add ~/.ssh/id_ed25519_personal
ssh-add ~/.ssh/id_ed25519_work
```

**Шаг 3: Добавьте публичные ключи на соответствующие аккаунты GitHub**

**Личный:**
```bash
cat ~/.ssh/id_ed25519_personal.pub
```

**Рабочий:**
```bash
cat ~/.ssh/id_ed25519_work.pub
```

**Шаг 4: Создайте `~/.ssh/config`**

```bash
# Личный аккаунт
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_personal
  IdentitiesOnly yes

# Рабочий аккаунт
Host github-work
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_work
  IdentitiesOnly yes
```

**Шаг 5: Использование**

**Личный репозиторий (стандартно):**
```bash
git clone git@github.com:personal-user/repo.git
```

**Рабочий репозиторий (через алиас):**
```bash
git clone git@github-work:company/repo.git
```

**Для существующих репозиториев:**
```bash
git remote set-url origin git@github-work:company/repo.git
```

**Шаг 6: Настройте user.name и user.email для каждого репозитория**

**В личном репозитории:**
```bash
cd ~/personal-project
git config user.name "Suheil"
git config user.email "personal@example.com"
```

**В рабочем репозитории:**
```bash
cd ~/work-project
git config user.name "Suheil (Company)"
git config user.email "work@company.com"
```

✅ **Готово!** Теперь каждый репозиторий использует правильный ключ и идентификацию.

---

## Дополнительные настройки

### Проверка использованного ключа

```bash
ssh -vT git@github.com 2>&1 | grep "Offering public key"
```

**Вывод:**
```
debug1: Offering public key: /c/Users/londo/.ssh/id_ed25519 ED25519
```

### Удаление ключа из ssh-agent

```bash
ssh-add -D  # Удалить все ключи
ssh-add -d ~/.ssh/id_ed25519  # Удалить конкретный ключ
```

### Смена passphrase для существующего ключа

```bash
ssh-keygen -p -f ~/.ssh/id_ed25519
```

### Резервное копирование ключей

⚠️ **Важно:** Сделайте резервную копию приватного ключа!

**Windows:**
```bash
cp ~/.ssh/id_ed25519 /d/Backups/ssh-key-backup
cp ~/.ssh/id_ed25519.pub /d/Backups/ssh-key-backup
```

**Храните резервную копию в безопасном месте (не в облаке!).**

---

## Проверочный чеклист

✅ **SSH ключ создан:**
```bash
ls ~/.ssh/id_ed25519*
```

✅ **ssh-agent запущен:**
```bash
ssh-add -l
```

✅ **Публичный ключ добавлен на GitHub:**
GitHub → Settings → SSH and GPG keys

✅ **Подключение работает:**
```bash
ssh -T git@github.com
# Hi Suheil! You've successfully authenticated...
```

✅ **Репозиторий использует SSH:**
```bash
git remote -v
# origin  git@github.com:username/repo.git
```

✅ **Коммит и push работают:**
```bash
git add .
git commit -m "Test SSH"
git push
```

---

## Полезные команды

| Команда | Описание |
|---------|----------|
| `ssh-keygen -t ed25519 -C "email"` | Создать новый SSH ключ |
| `eval "$(ssh-agent -s)"` | Запустить ssh-agent |
| `ssh-add ~/.ssh/id_ed25519` | Добавить ключ в ssh-agent |
| `ssh-add -l` | Список ключей в ssh-agent |
| `ssh-add -D` | Удалить все ключи из ssh-agent |
| `cat ~/.ssh/id_ed25519.pub` | Показать публичный ключ |
| `clip < ~/.ssh/id_ed25519.pub` | Скопировать публичный ключ |
| `ssh -T git@github.com` | Тест подключения к GitHub |
| `ssh -vT git@github.com` | Подробный вывод (debug) |
| `git remote set-url origin git@github.com:user/repo.git` | Сменить remote на SSH |

---

## Заключение

SSH — это стандартный и безопасный способ работы с GitHub. После первоначальной настройки вы забудете о проблемах с паролями и токенами.

✅ **Преимущества:**
- Не нужно вводить пароль при каждом push
- Безопаснее, чем пароль
- Поддерживает несколько аккаунтов

⚠️ **Важно:**
- Храните приватный ключ в безопасности
- Не делитесь приватным ключом
- Делайте резервные копии ключей
- Используйте passphrase на общих компьютерах

🎯 **Для туристического бизнеса в ОАЭ:**
SSH упрощает совместную работу над проектами. Настройте один раз — работайте эффективно!
