# GitHub Flow Diagram - Полный процесс работы с GitHub

## Базовый GitHub Flow

```
┌──────────┐    ┌───────┐    ┌────────┐    ┌────────┐    ┌──────┐    ┌────────┐    ┌───────┐    ┌───────┐
│  FORK    │───▶│ CLONE │───▶│ BRANCH │───▶│ COMMIT │───▶│ PUSH │───▶│   PR   │───▶│ REVIEW│───▶│ MERGE │
│(optional)│    │       │    │        │    │        │    │      │    │        │    │       │    │       │
└──────────┘    └───────┘    └────────┘    └────────┘    └──────┘    └────────┘    └───────┘    └───────┘
   Создай         Скачай      Создай        Сохрани       Отправь     Создай       Code         Влей в
   свою копию     локально    ветку         изменения     на GitHub   Pull         Review       main
                                                                       Request
```

---

## Детальная схема с примерами команд

### 1. Fork (для open-source проектов)

```
┌──────────────────────────────┐
│  Original Repository         │
│  github.com/author/project   │
└──────────────────────────────┘
              │
              │ Fork (через UI)
              ▼
┌──────────────────────────────┐
│  Your Fork                   │
│  github.com/you/project      │
└──────────────────────────────┘
```

**Действие:** Нажми кнопку **Fork** на GitHub

---

### 2. Clone (скачивание репозитория)

```
┌──────────────────────────────┐
│  GitHub                      │
│  github.com/you/project      │
└──────────────────────────────┘
              │
              │ git clone https://github.com/you/project.git
              ▼
┌──────────────────────────────┐
│  Local Machine               │
│  C:/projects/project/        │
│                              │
│  - .git/                     │
│  - src/                      │
│  - README.md                 │
└──────────────────────────────┘
```

**Команда:**
```bash
git clone https://github.com/username/project.git
cd project
```

---

### 3. Branch (создание ветки для работы)

```
main:    A───B───C  (не трогаем!)
              \
              git checkout -b feature/add-login
              \
feature:       C  (HEAD - начинаем работу здесь)
```

**Команда:**
```bash
git checkout -b feature/add-login
```

**Правило:** Никогда не работай в main напрямую!

---

### 4. Commit (сохранение изменений локально)

```
feature: C───D───E───F  (HEAD)
         ↑   ↑   ↑   ↑
         │   │   │   └─ git commit -m "Add tests"
         │   │   └───── git commit -m "Style login form"
         │   └────────── git commit -m "Add login form"
         └────────────── Начальный commit (от main)
```

**Команды:**
```bash
# 1. Внеси изменения в файлы
code src/Login.jsx

# 2. Добавь в staging
git add src/Login.jsx

# 3. Коммит
git commit -m "Add login form"

# 4. Повторяй для каждого логического изменения
```

---

### 5. Push (отправка на GitHub)

```
┌──────────────────────────────┐
│  Local Repository            │
│                              │
│  feature: C───D───E───F      │
└──────────────────────────────┘
              │
              │ git push origin feature/add-login
              ▼
┌──────────────────────────────┐
│  GitHub (origin)             │
│                              │
│  feature: C───D───E───F      │
└──────────────────────────────┘
```

**Команда:**
```bash
git push origin feature/add-login
```

---

### 6. Pull Request (предложение изменений)

```
GitHub UI:

┌─────────────────────────────────────────────┐
│  Pull Request                               │
├─────────────────────────────────────────────┤
│  base: main  ◄───  compare: feature/add-login│
│                                             │
│  Title: Add login functionality             │
│  Description:                               │
│  - Added login form                         │
│  - Added authentication                     │
│  - Added tests                              │
│                                             │
│  [Create Pull Request]                      │
└─────────────────────────────────────────────┘
```

**Действие:** На GitHub нажми **New Pull Request**

---

### 7. Code Review (проверка кода)

```
┌──────────────────────────────────────┐
│  Pull Request #123                   │
├──────────────────────────────────────┤
│                                      │
│  👤 Reviewer 1: "LGTM!" ✅           │
│  👤 Reviewer 2: "Change X" 💬        │
│  👤 Author: "Fixed!" ✅               │
│                                      │
│  Files changed: 3                    │
│  Commits: 4                          │
│  Checks: ✅ All passed               │
│                                      │
│  [Merge pull request ▼]              │
└──────────────────────────────────────┘
```

**Процесс:**
1. Reviewer оставляет комментарии
2. Ты исправляешь замечания
3. Push изменений (PR обновится автоматически)
4. Reviewer одобряет

---

### 8. Merge (слияние в main)

```
До merge:

main:    A───B───C
              \
feature:       D───E───F

После merge:

main:    A───B───C───────M
              \         /
feature:       D───E───F
```

**Действие:** На GitHub нажми **Merge pull request**

**Типы merge:**
- **Merge commit** - создает merge commit M
- **Squash and merge** - все коммиты D,E,F в один
- **Rebase and merge** - линейная история

---

## Полный цикл с командами

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ВЕСЬ ПРОЦЕСС                                 │
└─────────────────────────────────────────────────────────────────────┘

# 1. CLONE
git clone https://github.com/username/project.git
cd project

# 2. BRANCH
git checkout -b feature/my-feature

# 3. WORK
code src/file.js
npm test

# 4. COMMIT
git add .
git commit -m "Add feature X"

# 5. PUSH
git push origin feature/my-feature

# 6. PR (через GitHub UI)
- Открой GitHub
- New Pull Request
- Заполни описание
- Create Pull Request

# 7. CODE REVIEW
- Жди review
- Исправляй замечания
- git commit + git push (PR обновится)

# 8. MERGE (через GitHub UI)
- Reviewer нажимает Merge
- Feature влита в main

# 9. CLEANUP
git checkout main
git pull origin main
git branch -d feature/my-feature
```

---

## Fork Workflow (для open-source)

```
┌───────────────────────────────────────────────────────────────────┐
│                  ORIGINAL REPOSITORY                               │
│                  github.com/author/project                         │
│                                                                    │
│  main: A───B───C───D───E                                          │
└───────────────────────────────────────────────────────────────────┘
                         ▲
                         │ upstream
                         │
┌────────────────────────┼────────────────────────────────────────┐
│  YOUR FORK             │                                         │
│  github.com/you/project│                                         │
│                        │                                         │
│  main: A───B───C───D───E  (синхронизирован)                    │
│              \                                                   │
│  feature:     F───G───H   (твоя работа)                         │
└──────────────────────────────────────────────────────────────────┘
                         │
                         │ origin
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  LOCAL MACHINE                                                    │
│                                                                   │
│  main: A───B───C───D───E                                         │
│              \                                                    │
│  feature:     F───G───H  (HEAD)                                  │
└──────────────────────────────────────────────────────────────────┘

КОМАНДЫ:

# Добавь upstream
git remote add upstream https://github.com/author/project.git

# Синхронизируй main
git fetch upstream
git checkout main
git merge upstream/main

# Работай в feature
git checkout -b feature/my-contribution
# ... изменения ...
git push origin feature/my-contribution

# Создай PR в оригинальный репозиторий (через GitHub UI)
```

---

## Защищенная ветка main (Branch Protection)

```
GitHub Settings → Branches → Branch protection rules:

main:
├─ ✅ Require pull request before merging
├─ ✅ Require approvals (минимум 1)
├─ ✅ Require status checks to pass
├─ ✅ Require conversation resolution
└─ ❌ Allow force pushes (ЗАПРЕЩЕНО!)

Результат:

git push origin main  ❌  ERROR: Protected branch!

Правильный путь:
feature → PR → Review → Merge ✅
```

---

## CI/CD в GitHub Flow

```
┌───────────────────────────────────────────────────────────────┐
│  PUSH                                                          │
└───────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│  GITHUB ACTIONS (автоматически)                               │
│                                                                │
│  1. ✅ Run tests (npm test)                                   │
│  2. ✅ Run linters (eslint)                                   │
│  3. ✅ Build project (npm run build)                          │
│  4. ✅ Security scan                                          │
│                                                                │
│  All checks passed ✅                                         │
└───────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────────┐
│  PULL REQUEST                                                  │
│                                                                │
│  Status: ✅ All checks passed                                 │
│  [Merge pull request] (теперь можно merge)                    │
└───────────────────────────────────────────────────────────────┘
```

---

## Множественные Pull Requests

```
main:    A───B─────────────────M1──────────M2
              \               /          /
feature1:      C───D───E─────┘          /
                \                      /
feature2:        F───G───H───I───────┘

TIMELINE:
1. Создан feature1 (C,D,E)
2. Создан feature2 от B (F,G,H,I)
3. PR #1 (feature1) → merged (M1)
4. PR #2 (feature2) → merged (M2)

ПАРАЛЛЕЛЬНАЯ РАБОТА:
- feature1 и feature2 разрабатываются одновременно
- Каждая имеет свой PR
- Merge независимо друг от друга
```

---

## Draft Pull Request

```
┌───────────────────────────────────────────────┐
│  Pull Request #123 (DRAFT) 📝                │
├───────────────────────────────────────────────┤
│  This PR is a draft                           │
│  - Early feedback welcome                     │
│  - Not ready for merge                        │
│                                               │
│  [Mark as ready for review]                   │
└───────────────────────────────────────────────┘

Когда использовать:
- Хочешь показать прогресс
- Нужен ранний feedback
- Работа еще не завершена
```

---

## Revert через GitHub

```
main:    A───B───C───D  (D содержит баг!)

GitHub UI: Revert PR #123

main:    A───B───C───D───R  (R отменяет D)
                         ↑
                    Revert commit

Команда:
git revert D
```

---

## Чек-лист GitHub Flow

```
[ ] 1. Fork или Clone репозитория
[ ] 2. Создать feature ветку от main
[ ] 3. Сделать изменения
[ ] 4. Коммитить небольшими логическими частями
[ ] 5. Push в свою ветку
[ ] 6. Создать Pull Request
[ ] 7. Заполнить описание PR
[ ] 8. Пройти Code Review
[ ] 9. Исправить замечания (если есть)
[ ] 10. Дождаться прохождения CI/CD
[ ] 11. Получить approval
[ ] 12. Merge в main
[ ] 13. Удалить feature ветку
[ ] 14. Pull обновленный main локально
```

---

## GitHub Flow vs Git Flow

### GitHub Flow (упрощенный)
```
main:    A───B───────E  (всегда deployable)
              \     /
feature:       C───D
```
- Одна основная ветка (main)
- Короткоживущие feature ветки
- Быстрый релиз

### Git Flow (сложный)
```
main:     A───────E  (releases)
               /
develop:  A───B───C───D
               \   \
feature:        F   G
```
- Две основные ветки (main + develop)
- Долгоживущие ветки
- Запланированные релизы

---

## GitHub CLI для быстрого workflow

```bash
# Создание PR одной командой
gh pr create --title "Add feature" --body "Description"

# Просмотр PR
gh pr view 123

# Проверка статуса
gh pr status

# Merge PR
gh pr merge 123

# Checkout чужого PR для тестирования
gh pr checkout 123
```

---

## Заключение

**GitHub Flow - это:**

1. **Простота** - только main + feature ветки
2. **Скорость** - быстрые итерации
3. **Безопасность** - через Pull Request
4. **Code Review** - обязательная проверка
5. **CI/CD** - автоматические проверки
6. **Документация** - история в PR

**Основное правило:** Main всегда должен быть в рабочем состоянии (deployable)!
