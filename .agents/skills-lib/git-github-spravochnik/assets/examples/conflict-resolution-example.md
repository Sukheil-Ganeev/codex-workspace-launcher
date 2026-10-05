# Conflict Resolution Example - Разрешение merge конфликтов

## Введение

**Ситуация:** Ты работал над фичей `feature/add-user-profile` 3 дня. Параллельно твой коллега работал над `feature/add-settings`. Оба изменили один и тот же файл `src/components/Header.jsx`.

Когда ты пытаешься влить свою ветку в `develop`, Git не может автоматически объединить изменения - возникает **merge conflict**.

**Цель:** Научиться правильно разрешать конфликты, сохраняя изменения обеих веток.

---

## Как возникают конфликты

### Шаг 1: Начальное состояние (3 дня назад)

**Файл:** `src/components/Header.jsx` в ветке `develop`

```javascript
function Header() {
  return (
    <header>
      <Logo />
      <Navigation />
    </header>
  );
}
```

### Шаг 2: Твои изменения (feature/add-user-profile)

Ты добавил кнопку профиля:

```javascript
function Header() {
  return (
    <header>
      <Logo />
      <Navigation />
      <UserProfileButton />  {/* ← Твоё изменение */}
    </header>
  );
}
```

### Шаг 3: Изменения коллеги (feature/add-settings)

Коллега добавил кнопку настроек и уже влил в `develop`:

```javascript
function Header() {
  return (
    <header>
      <Logo />
      <Navigation />
      <SettingsButton />  {/* ← Изменение коллеги */}
    </header>
  );
}
```

### Шаг 4: Конфликт при merge

Когда ты пытаешься влить свою ветку:

```bash
git checkout develop
git pull origin develop
git merge feature/add-user-profile
```

**Результат:**
```
Auto-merging src/components/Header.jsx
CONFLICT (content): Merge conflict in src/components/Header.jsx
Automatic merge failed; fix conflicts and then commit the result.
```

**Причина:** Git не знает, какую кнопку оставить - твою (`UserProfileButton`) или коллеги (`SettingsButton`).

---

## Пошаговое разрешение конфликта

### Шаг 1: Проверка состояния

```bash
# Посмотри статус после конфликта
git status
```

**Вывод:**
```
On branch develop
Your branch is up to date with 'origin/develop'.

You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   src/components/Header.jsx

no changes added to commit (use "git add" and/or "git commit -a")
```

**Что это значит:**
- `both modified` - файл изменен в обеих ветках
- Git ждет, что ты вручную разрешишь конфликт
- Можно отменить merge через `git merge --abort`

---

### Шаг 2: Открой файл с конфликтом

Открой `src/components/Header.jsx` в редакторе.

**Содержимое файла с маркерами конфликта:**

```javascript
function Header() {
  return (
    <header>
      <Logo />
      <Navigation />
<<<<<<< HEAD
      <SettingsButton />
=======
      <UserProfileButton />
>>>>>>> feature/add-user-profile
    </header>
  );
}
```

**Разбор маркеров:**

```
<<<<<<< HEAD
  Код из текущей ветки (develop)
  Изменения коллеги (SettingsButton)
=======
  Код из вливаемой ветки (feature/add-user-profile)
  Твои изменения (UserProfileButton)
>>>>>>> feature/add-user-profile
```

---

### Шаг 3: Анализ ситуации

**Вопросы для принятия решения:**

1. **Что хотели сделать оба разработчика?**
   - Коллега: Добавить кнопку настроек
   - Ты: Добавить кнопку профиля

2. **Нужны ли обе кнопки?**
   - Да, обе фичи независимы

3. **В каком порядке их расположить?**
   - Логично: Navigation → Settings → Profile (слева направо)

---

### Шаг 4: Ручное разрешение конфликта

Удали маркеры конфликта и объедини изменения:

**До разрешения:**
```javascript
<<<<<<< HEAD
      <SettingsButton />
=======
      <UserProfileButton />
>>>>>>> feature/add-user-profile
```

**После разрешения:**
```javascript
      <SettingsButton />
      <UserProfileButton />
```

**Полный файл после разрешения:**
```javascript
function Header() {
  return (
    <header>
      <Logo />
      <Navigation />
      <SettingsButton />       {/* Изменение коллеги */}
      <UserProfileButton />    {/* Твоё изменение */}
    </header>
  );
}
```

---

### Шаг 5: Сохрани и проверь синтаксис

```bash
# Проверь, что код компилируется
npm run build

# Или запусти dev server
npm start
```

**Важно:** Убедись, что:
- Удалены ВСЕ маркеры конфликта (`<<<<<<<`, `=======`, `>>>>>>>`)
- Код синтаксически корректен
- Приложение запускается без ошибок

---

### Шаг 6: Добавь разрешенный файл в staging

```bash
# Отметь конфликт как разрешенный
git add src/components/Header.jsx

# Проверь статус
git status
```

**Вывод:**
```
On branch develop
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)

Changes to be committed:
        modified:   src/components/Header.jsx
```

**Что произошло:**
- `git add` сигнализирует Git, что конфликт разрешен
- Файл готов для финального merge commit

---

### Шаг 7: Завершение merge

```bash
# Создай merge commit
git commit
```

Git откроет редактор с автоматическим сообщением:

```
Merge branch 'feature/add-user-profile' into develop

# Conflicts:
#       src/components/Header.jsx
```

**Улучши сообщение:**

```
Merge branch 'feature/add-user-profile' into develop

Разрешен конфликт в Header.jsx:
- Сохранена кнопка настроек (из develop)
- Добавлена кнопка профиля (из feature/add-user-profile)
- Обе кнопки работают корректно

Протестировано:
- Settings открываются корректно
- User Profile отображает данные пользователя
```

Сохрани и закрой редактор.

**Вывод:**
```
[develop a1b2c3d] Merge branch 'feature/add-user-profile' into develop
```

---

### Шаг 8: Отправка на GitHub

```bash
# Отправь изменения на сервер
git push origin develop
```

**Вывод:**
```
Enumerating objects: 10, done.
Counting objects: 100% (10/10), done.
Delta compression using up to 8 threads
Compressing objects: 100% (6/6), done.
Writing objects: 100% (6/6), 842 bytes | 842.00 KiB/s, done.
Total 6 (delta 4), reused 0 (delta 0)
To github.com:username/project.git
   abc1234..a1b2c3d  develop -> develop
```

---

## Сложный конфликт: Удаление vs Изменение

### Ситуация

**Твоя ветка:** Удалила функцию `calculateDiscount()`
**Ветка коллеги:** Изменила ту же функцию (добавила новый параметр)

### Конфликт

```javascript
function ProductCard({ product }) {
  const price = product.price;
<<<<<<< HEAD
  // calculateDiscount() удалена - теперь скидки на бэкенде
=======
  const discount = calculateDiscount(product.price, product.category);
  const finalPrice = price - discount;
>>>>>>> feature/backend-discounts

  return <div>{price}</div>;
}
```

### Разрешение

Нужно понять **почему** функция удалена:

1. **Поговори с коллегой** (или посмотри его commit message)
2. **Если логика переехала на бэкенд** - удали вызов функции
3. **Если нужна для других частей** - оставь функцию, но не используй здесь

**Правильное разрешение (логика на бэкенде):**

```javascript
function ProductCard({ product }) {
  // Цена уже с учетом скидки приходит с бэкенда
  const price = product.finalPrice;

  return <div>{price}</div>;
}
```

---

## Конфликт в нескольких файлах

```bash
git merge feature/refactor-api

# Вывод:
# CONFLICT: src/api/users.js
# CONFLICT: src/api/products.js
# CONFLICT: src/api/orders.js
```

**Стратегия:** Разрешай по одному файлу, используй `git add` после каждого, затем `git commit`.

---

## Конфликт при rebase

```bash
git rebase develop

# CONFLICT в src/App.js

# Разрешение:
code src/App.js  # Разреши конфликт
git add src/App.js
git rebase --continue  # НЕ git commit!
```

**Отличие от merge:** В rebase используй `git rebase --continue`, а не `git commit`.

---

## VS Code для разрешения конфликтов

VS Code показывает кнопки:
- **Accept Current Change** - текущая ветка
- **Accept Incoming Change** - вливаемая ветка
- **Accept Both Changes** - обе
- **Compare Changes** - diff

---

## Отмена merge при конфликте

```bash
# Если конфликт слишком сложный
git merge --abort

# Для rebase
git rebase --abort
```

---

## Типичные ошибки

### Ошибка 1: Забыл удалить маркеры

```javascript
// НЕПРАВИЛЬНО: маркеры остались
<<<<<<< HEAD
code
=======
```

**Результат:** Синтаксическая ошибка.

### Ошибка 2: Удалил чужие изменения

**Всегда объединяй изменения обеих веток**, не удаляй работу коллег.

### Ошибка 3: Не протестировал

**Всегда:** `npm test` и `npm start` после разрешения конфликта.

---

## Превентивные меры

1. **Частые pull из develop** - конфликты будут мелкими
2. **Разделяй файлы** - не меняй одни и те же файлы
3. **Общайся с командой** - договаривайтесь кто первый вольет изменения

---

## Чек-лист разрешения конфликтов

```
[ ] git status - посмотреть конфликтные файлы
[ ] Открыть файл с конфликтом
[ ] Найти маркеры <<<<<<<, =======, >>>>>>>
[ ] Понять изменения обеих веток
[ ] Объединить изменения (не удалять чужие!)
[ ] Удалить ВСЕ маркеры
[ ] Проверить синтаксис
[ ] git add <файл>
[ ] Повторить для всех файлов
[ ] npm test
[ ] npm start
[ ] git commit
[ ] git push
```

---

## Полная последовательность команд

```bash
# 1. Merge с конфликтом
git checkout develop
git pull origin develop
git merge feature/my-feature
# CONFLICT!

# 2. Проверка
git status

# 3. Разрешение
code src/App.js
# ... удали маркеры, объедини изменения ...

# 4. Проверка кода
npm test

# 5. Добавление
git add src/App.js

# 6. Финализация
git commit

# 7. Push
git push origin develop
```

---

## Заключение

Конфликты - это нормально! Главное:
1. Не паниковать
2. Внимательно читать маркеры
3. Понимать логику изменений
4. Удалять ВСЕ маркеры
5. Тестировать после разрешения
6. Писать понятный commit message

**Практика делает мастера!**
