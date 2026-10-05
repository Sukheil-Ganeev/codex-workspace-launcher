# Feature Branch Workflow
## Полный пример разработки новой функции

Этот документ показывает полный цикл работы над новой функцией от создания ветки до merge в main.

---

## Сценарий

**Задача:** Добавить функцию регистрации пользователей в веб-приложение

**Issue:** #42 - Add user registration feature

**Команда:** 2 разработчика (ты и коллега), 1 ревьюер

---

## Этап 1: Подготовка (Preparation)

### 1.1 Проверка текущего состояния

```bash
# Проверяем на какой ветке мы находимся
git branch
# * main

# Проверяем статус (должно быть чисто)
git status
# On branch main
# Your branch is up to date with 'origin/main'.
# nothing to commit, working tree clean

# Проверяем последние коммиты
git log --oneline -5
```

### 1.2 Обновление main ветки

```bash
# Получаем последние изменения с remote
git fetch origin

# Переключаемся на main (если не на ней)
git checkout main

# Обновляем main с remote
git pull origin main
# или просто
git pull
```

**Результат:**
```
From https://github.com/username/project
 * branch            main       -> FETCH_HEAD
Already up to date.
```

---

## Этап 2: Создание feature ветки

### 2.1 Именование ветки

**Правила именования:**
- Используй `feature/` префикс для новых функций
- Краткое описание на английском
- Через дефис, без пробелов
- Можно добавить номер issue

**Примеры:**
- ✓ `feature/user-registration`
- ✓ `feature/42-user-registration`
- ✓ `feature/add-login-form`
- ✗ `user registration` (есть пробелы)
- ✗ `my-feature` (неинформативно)

### 2.2 Создание и переключение

```bash
# Вариант 1: Две команды
git branch feature/user-registration
git checkout feature/user-registration

# Вариант 2: Одна команда (рекомендуется)
git checkout -b feature/user-registration

# Проверка
git branch
#   main
# * feature/user-registration
```

**Совет для Windows + Git Bash:**
Если имя ветки содержит слеши, Git Bash обработает их правильно.

---

## Этап 3: Разработка (Development)

### 3.1 Создание новых файлов

Создаем структуру для функции регистрации:

```bash
# Создаем директорию для компонентов (если в Unix/Git Bash)
mkdir -p src/components/auth

# Создаем файлы
touch src/components/auth/RegisterForm.jsx
touch src/components/auth/RegisterForm.css
touch src/api/userService.js
```

**В Windows можно использовать:**
```bash
# Через File Explorer или
echo. > src/components/auth/RegisterForm.jsx
```

### 3.2 Написание кода

**RegisterForm.jsx:**
```javascript
import React, { useState } from 'react';
import './RegisterForm.css';
import { registerUser } from '../../api/userService';

export default function RegisterForm() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await registerUser(formData);
      alert('Registration successful!');
    } catch (error) {
      alert('Registration failed: ' + error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Username"
        value={formData.username}
        onChange={(e) => setFormData({...formData, username: e.target.value})}
      />
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
      />
      <input
        type="password"
        placeholder="Password"
        value={formData.password}
        onChange={(e) => setFormData({...formData, password: e.target.value})}
      />
      <button type="submit">Register</button>
    </form>
  );
}
```

**userService.js:**
```javascript
const API_URL = 'https://api.example.com';

export async function registerUser(userData) {
  const response = await fetch(`${API_URL}/users/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  });

  if (!response.ok) {
    throw new Error('Registration failed');
  }

  return response.json();
}
```

### 3.3 Проверка изменений

```bash
# Проверяем что изменилось
git status
```

**Вывод:**
```
On branch feature/user-registration
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        src/components/auth/RegisterForm.jsx
        src/components/auth/RegisterForm.css
        src/api/userService.js

nothing added to commit but untracked files present (use "git add" to track)
```

---

## Этап 4: Первый коммит

### 4.1 Добавление файлов в staging

```bash
# Вариант 1: Добавить все новые файлы
git add .

# Вариант 2: Добавить конкретные файлы (безопаснее)
git add src/components/auth/RegisterForm.jsx
git add src/components/auth/RegisterForm.css
git add src/api/userService.js

# Проверка staging area
git status
```

**Вывод:**
```
On branch feature/user-registration
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   src/api/userService.js
        new file:   src/components/auth/RegisterForm.css
        new file:   src/components/auth/RegisterForm.jsx
```

### 4.2 Создание коммита

```bash
# Хороший commit message
git commit -m "feat(auth): add user registration form and API service"

# Или более детальный (откроется редактор)
git commit
```

**В редакторе напиши:**
```
feat(auth): add user registration form and API service

- Created RegisterForm component with username, email, password fields
- Implemented userService with registerUser API call
- Added basic styling for registration form

Refs #42
```

**Результат:**
```
[feature/user-registration a1b2c3d] feat(auth): add user registration form and API service
 3 files changed, 85 insertions(+)
 create mode 100644 src/api/userService.js
 create mode 100644 src/components/auth/RegisterForm.css
 create mode 100644 src/components/auth/RegisterForm.jsx
```

---

## Этап 5: Продолжение разработки

### 5.1 Добавление валидации

Редактируем RegisterForm.jsx, добавляем валидацию:

```javascript
// ... (добавляем функцию валидации)
const validateForm = () => {
  if (formData.username.length < 3) {
    alert('Username must be at least 3 characters');
    return false;
  }
  if (!formData.email.includes('@')) {
    alert('Invalid email');
    return false;
  }
  if (formData.password.length < 6) {
    alert('Password must be at least 6 characters');
    return false;
  }
  return true;
};

const handleSubmit = async (e) => {
  e.preventDefault();
  if (!validateForm()) return;
  // ... rest of the code
};
```

### 5.2 Проверка и коммит изменений

```bash
# Проверяем что изменилось
git status
# modified:   src/components/auth/RegisterForm.jsx

# Смотрим детали изменений
git diff src/components/auth/RegisterForm.jsx

# Добавляем и коммитим
git add src/components/auth/RegisterForm.jsx
git commit -m "feat(auth): add form validation to registration"
```

### 5.3 Добавление тестов

Создаем файл тестов:

```bash
touch src/components/auth/RegisterForm.test.js
```

**RegisterForm.test.js:**
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import RegisterForm from './RegisterForm';

test('displays validation error for short username', () => {
  render(<RegisterForm />);
  const usernameInput = screen.getByPlaceholderText('Username');
  const submitButton = screen.getByText('Register');

  fireEvent.change(usernameInput, { target: { value: 'ab' } });
  fireEvent.click(submitButton);

  // Ожидаем alert с ошибкой
});
```

```bash
# Добавляем и коммитим тесты
git add src/components/auth/RegisterForm.test.js
git commit -m "test(auth): add validation tests for registration form"
```

---

## Этап 6: Просмотр истории

```bash
# Просмотр всех коммитов в ветке
git log --oneline

# Вывод:
# d4e5f6g test(auth): add validation tests for registration form
# a1b2c3d feat(auth): add form validation to registration
# 7h8i9j0 feat(auth): add user registration form and API service

# Детальный просмотр последнего коммита
git show

# Просмотр изменений относительно main
git diff main
```

---

## Этап 7: Push в remote репозиторий

### 7.1 Первый push (создание remote ветки)

```bash
# Push с созданием upstream ветки
git push -u origin feature/user-registration

# Или полная форма
git push --set-upstream origin feature/user-registration
```

**Вывод:**
```
Enumerating objects: 15, done.
Counting objects: 100% (15/15), done.
Delta compression using up to 8 threads
Compressing objects: 100% (12/12), done.
Writing objects: 100% (13/13), 2.45 KiB | 2.45 MiB/s, done.
Total 13 (delta 5), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (5/5), completed with 2 local objects.
remote:
remote: Create a pull request for 'feature/user-registration' on GitHub by visiting:
remote:      https://github.com/username/project/pull/new/feature/user-registration
remote:
To https://github.com/username/project.git
 * [new branch]      feature/user-registration -> feature/user-registration
Branch 'feature/user-registration' set up to track remote branch 'feature/user-registration' from 'origin'.
```

### 7.2 Последующие push'ы

```bash
# После -u достаточно просто
git push

# Git уже знает куда пушить
```

---

## Этап 8: Создание Pull Request

### 8.1 Через GitHub Web UI

1. Перейди на https://github.com/username/project
2. Увидишь banner: "feature/user-registration had recent pushes"
3. Нажми "Compare & pull request"
4. Заполни форму PR:

**Title:**
```
Add user registration feature
```

**Description:**
```markdown
## What changed
Added user registration functionality with form validation and API integration.

## Features
- Registration form with username, email, password fields
- Client-side validation
- API service for user registration
- Unit tests for form validation

## How to test
1. Run the app: `npm start`
2. Navigate to `/register`
3. Try to register with invalid data (short username, invalid email)
4. Verify validation errors appear
5. Register with valid data
6. Verify successful registration

## Checklist
- [x] Code follows style guide
- [x] Tests added
- [x] Documentation updated
- [x] All tests pass

Closes #42
```

5. Выбери reviewers
6. Добавь labels (enhancement, frontend)
7. Нажми "Create pull request"

### 8.2 Через GitHub CLI (альтернатива)

```bash
# Если установлен gh CLI
gh pr create --title "Add user registration feature" --body "..."

# Интерактивный режим
gh pr create --web
```

---

## Этап 9: Code Review процесс

### 9.1 Ревьюер оставляет комментарии

**Комментарий 1:**
> В RegisterForm.jsx используются alert'ы для ошибок. Лучше использовать toast notifications или error messages в UI.

**Комментарий 2:**
> Не хватает обработки loading состояния при отправке формы.

### 9.2 Внесение изменений по ревью

```bash
# Убедись что на feature ветке
git branch
# * feature/user-registration

# Вносим изменения в код
# ... (редактируем файлы)

# Проверяем изменения
git status
git diff

# Коммитим исправления
git add src/components/auth/RegisterForm.jsx
git commit -m "refactor(auth): replace alerts with toast notifications and add loading state"

# Пушим изменения
git push
```

**Важно:** Изменения автоматически появятся в существующем PR!

### 9.3 Обновление ветки с main (если main изменился)

```bash
# Получаем изменения с remote
git fetch origin

# Вариант 1: Merge (создаст merge commit)
git merge origin/main

# Вариант 2: Rebase (чище история)
git rebase origin/main

# Если есть конфликты, разреши их и продолжи:
# ... (исправляем конфликты)
git add .
git rebase --continue

# Пушим обновленную ветку
git push --force-with-lease
```

---

## Этап 10: Approval и Merge

### 10.1 Ревьюер одобряет PR

На GitHub PR появляется:
```
✓ johndoe approved these changes
```

### 10.2 Проверка CI/CD

Дождись прохождения всех checks:
```
✓ All checks have passed
  ✓ Build (3m 24s)
  ✓ Tests (1m 52s)
  ✓ Lint (45s)
```

### 10.3 Merge PR

**Через GitHub UI:**

1. Нажми "Merge pull request"
2. Выбери тип merge:
   - **Merge commit** - создаст merge commit (сохраняет всю историю)
   - **Squash and merge** - объединит все коммиты в один (чище история)
   - **Rebase and merge** - перебазирует коммиты (линейная история)

3. Подтверди merge
4. Опционально: удали ветку на GitHub

**Через командную строку:**

```bash
# Переключись на main
git checkout main

# Обнови main
git pull origin main

# Смержь feature ветку
git merge feature/user-registration

# Запуш main
git push origin main
```

---

## Этап 11: Cleanup (очистка)

### 11.1 Обновление локального main

```bash
# Переключаемся на main
git checkout main

# Получаем изменения после merge
git pull origin main
```

### 11.2 Удаление feature ветки

```bash
# Удаление локальной ветки
git branch -d feature/user-registration

# Если ветка не смержена и нужно удалить принудительно
git branch -D feature/user-registration

# Удаление remote ветки (если не удалена через GitHub)
git push origin --delete feature/user-registration
```

### 11.3 Проверка чистоты

```bash
# Проверяем оставшиеся ветки
git branch -a

# Вывод:
# * main
#   remotes/origin/main

# Проверяем статус
git status
# On branch main
# Your branch is up to date with 'origin/main'.
# nothing to commit, working tree clean
```

---

## Полная последовательность команд

```bash
# 1. Подготовка
git checkout main
git pull origin main

# 2. Создание ветки
git checkout -b feature/user-registration

# 3. Разработка
# ... (создание/редактирование файлов)
git add .
git commit -m "feat(auth): add user registration form and API service"

# 4. Дополнительные изменения
# ... (редактирование)
git add .
git commit -m "feat(auth): add form validation"

# 5. Push
git push -u origin feature/user-registration

# 6. Создание PR через GitHub UI

# 7. Изменения по ревью
# ... (редактирование)
git add .
git commit -m "refactor(auth): implement review feedback"
git push

# 8. После merge
git checkout main
git pull origin main
git branch -d feature/user-registration
git push origin --delete feature/user-registration
```

---

## Лучшие практики

1. **Маленькие коммиты**: Коммить логически связанные изменения
2. **Хорошие сообщения**: Использовать понятные commit messages
3. **Регулярные push'ы**: Пушить изменения минимум раз в день
4. **Актуальность ветки**: Регулярно обновлять ветку с main
5. **Self-review**: Проверять свой код перед созданием PR
6. **Тесты**: Всегда добавлять тесты для новой функциональности
7. **Документация**: Обновлять документацию вместе с кодом

---

## Частые ошибки

❌ **Работа напрямую в main**
```bash
# Плохо
git checkout main
# ... делаем изменения
git commit -m "changes"
```

✓ **Всегда используй feature ветки**
```bash
# Хорошо
git checkout -b feature/my-feature
# ... делаем изменения
git commit -m "feat: add feature"
```

❌ **Слишком большие PR**
- PR с 50+ файлами сложно ревьюить

✓ **Делить большие фичи на части**
- PR #1: Backend API
- PR #2: Frontend components
- PR #3: Integration tests

❌ **Push с --force на shared ветках**
```bash
# Опасно на main!
git push --force origin main
```

✓ **Использовать --force-with-lease на feature ветках**
```bash
# Безопаснее
git push --force-with-lease origin feature/my-feature
```
