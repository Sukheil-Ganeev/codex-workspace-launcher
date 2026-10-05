# Branches (ветки) — Полное руководство

Подробное руководство по работе с ветками в Git: создание, переключение, слияние, rebase, разрешение конфликтов и best practices.

---

## Содержание

1. [Что такое ветки и зачем они нужны](#что-такое-ветки-и-зачем-они-нужны)
2. [git branch — Создание веток](#git-branch--создание-веток)
3. [git checkout / git switch — Переключение](#git-checkout--переключение)
4. [git merge — Слияние веток](#git-merge--слияние-веток)
5. [Merge conflicts — Разрешение конфликтов](#merge-conflicts--разрешение-конфликтов)
6. [git rebase — Альтернатива merge](#git-rebase--альтернатива-merge)
7. [Best practices для веток](#best-practices-для-веток)

---

## Что такое ветки и зачем они нужны

**Ветки (branches)** позволяют работать над разными функциями параллельно без конфликтов.

**Зачем использовать ветки:**

1. **Изоляция:** Разработка новой функции не влияет на основной код
2. **Параллельная работа:** Команда работает над разными задачами одновременно
3. **Экспериментирование:** Можно тестировать идеи без риска сломать основной код
4. **Code review:** Pull requests основаны на ветках

**Визуализация:**

```
main:     A---B---C---F---G
               \       /
feature:        D-----E
```

---

## git branch — Создание веток

**Основные команды:**

```bash
# Просмотр всех веток
git branch

# Просмотр всех веток (включая удаленные)
git branch -a

# Создание новой ветки
git branch feature-login

# Удаление ветки
git branch -d feature-login

# Принудительное удаление (если не слита)
git branch -D feature-login

# Переименование текущей ветки
git branch -m new-name
```

---

## git checkout / git switch — Переключение

**Переключение между ветками:**

```bash
# Переключение на существующую ветку
git checkout main
git checkout feature-login

# Создание и переключение на новую ветку
git checkout -b feature-signup

# Эквивалентно:
git branch feature-signup
git checkout feature-signup
```

**Новый способ (Git 2.23+):**

```bash
# Переключение
git switch main

# Создание и переключение
git switch -c feature-signup
```

---

## git merge — Слияние веток

**Объединение веток:**

```bash
# 1. Переключитесь на ветку, в которую хотите слить (обычно main)
git checkout main

# 2. Слейте целевую ветку
git merge feature-login

# Вывод:
# Updating abc123..def456
# Fast-forward
#  login.html | 50 +++++++++++++++++++++++++++++++++++++++++
#  1 file changed, 50 insertions(+)
```

**Типы merge:**

1. **Fast-forward:** Прямое перемещение указателя (нет новых коммитов)
2. **3-way merge:** Создание merge commit (есть расхождения)

```
Fast-forward:
main:     A---B
               \
feature:        C---D

После merge:
main:     A---B---C---D


3-way merge:
main:     A---B---C
               \   \
feature:        D---E

После merge:
main:     A---B---C---F (merge commit)
               \     /
feature:        D---E
```

---

## Merge conflicts — Разрешение конфликтов

**Когда возникает конфликт:**

Две ветки изменили одни и те же строки в одном файле.

**Процесс разрешения (пошагово):**

**Шаг 1: Попытка слияния**

```bash
git merge feature-branch

# Вывод:
# Auto-merging index.html
# CONFLICT (content): Merge conflict in index.html
# Automatic merge failed; fix conflicts and then commit the result.
```

**Шаг 2: Просмотр конфликтующих файлов**

```bash
git status

# Вывод:
# Unmerged paths:
#   both modified:   index.html
```

**Шаг 3: Открытие конфликтующего файла**

Файл будет содержать маркеры конфликта:

```html
<!DOCTYPE html>
<html>
<head>
<<<<<<< HEAD
  <title>Главная страница</title>
=======
  <title>Home Page</title>
>>>>>>> feature-branch
</head>
</html>
```

**Расшифровка маркеров:**

- `<<<<<<< HEAD` — начало изменений в текущей ветке
- `=======` — разделитель
- `>>>>>>> feature-branch` — конец изменений в сливаемой ветке

**Шаг 4: Разрешение конфликта**

Выберите один из вариантов или объедините оба:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Главная страница - Home Page</title>
</head>
</html>
```

**Шаг 5: Добавление разрешенного файла**

```bash
git add index.html
```

**Шаг 6: Завершение merge**

```bash
git commit -m "Разрешен конфликт в index.html"
```

**Прерывание merge:**

```bash
# Если хотите отменить merge
git merge --abort
```

---

## git rebase — Альтернатива merge

**Rebase vs Merge:**

- **Merge:** Сохраняет историю, создает merge commit
- **Rebase:** Перемещает коммиты, создает линейную историю

**Использование rebase:**

```bash
# 1. Переключитесь на feature ветку
git checkout feature-branch

# 2. Rebase на main
git rebase main

# 3. Разрешите конфликты (если есть)
git add resolved-file.js
git rebase --continue

# 4. Отмена rebase (если нужно)
git rebase --abort
```

**Визуализация:**

```
До rebase:
main:     A---B---C
               \
feature:        D---E

После rebase:
main:     A---B---C
                   \
feature:            D'---E'
```

**ВНИМАНИЕ:** Не используйте rebase для публичных веток (где работают другие)!

---

## Best practices для веток

**Именование веток:**

| Тип | Префикс | Пример |
|-----|---------|--------|
| Новая функция | `feature/` | `feature/user-auth` |
| Исправление бага | `fix/` или `bugfix/` | `fix/login-error` |
| Хотфикс | `hotfix/` | `hotfix/critical-bug` |
| Релиз | `release/` | `release/v1.2.0` |
| Эксперимент | `experiment/` | `experiment/new-ui` |

**Workflow стратегии:**

1. **Feature Branch Workflow:**
   - Создать ветку для каждой функции
   - Слить в main через PR
   - Удалить ветку после слияния

2. **Git Flow:**
   - `main` — продакшн код
   - `develop` — разработка
   - `feature/*` — новые функции
   - `release/*` — подготовка релиза
   - `hotfix/*` — срочные исправления

**Команды для очистки:**

```bash
# Удаление локальных слитых веток
git branch --merged | grep -v "\*" | xargs git branch -d

# Удаление удаленной ветки
git push origin --delete feature-branch

# Очистка ссылок на удаленные ветки
git fetch --prune
```
