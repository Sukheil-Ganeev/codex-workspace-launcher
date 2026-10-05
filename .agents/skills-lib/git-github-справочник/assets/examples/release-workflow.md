# Release Workflow - Создание релиза проекта

## Введение

**Ситуация:** Твой проект готов к новому релизу. Нужно создать версию, tag, changelog и опубликовать на GitHub/npm.

**Цель:** Организованный процесс релиза с версионированием, документацией и автоматизацией.

---

## Semantic Versioning (SemVer)

Версии: MAJOR.MINOR.PATCH (например: 2.5.3)

**Правила:**
- **MAJOR** (2.0.0 → 3.0.0) - Breaking changes
- **MINOR** (2.5.0 → 2.6.0) - Новые фичи (обратно совместимые)
- **PATCH** (2.5.3 → 2.5.4) - Багфиксы

**Pre-release:**


---

## Шаг 1: Подготовка



Все должно быть зеленым!

---

## Шаг 2: Определение новой версии



**Анализ:** Есть новые фичи? → MINOR. Только багфиксы? → PATCH. Breaking changes? → MAJOR.

---

## Шаг 3: CHANGELOG

### Автоматический


added 56 packages, and audited 77 packages in 11s

11 packages are looking for funding
  run `npm fund` for details

6 moderate severity vulnerabilities

To address issues that do not require attention, run:
  npm audit fix

To address all issues (including breaking changes), run:
  npm audit fix --force

Run `npm audit` for details.

### Ручной

CHANGELOG.md:


---

## Шаг 4: Обновление версии

v1.0.1
v1.1.0
v2.0.0

Это обновит package.json и создаст tag.

---

## Шаг 5: Создание Tag



---

## Шаг 6: Push



---

## Шаг 7: GitHub Release

### Через UI

1. GitHub → Releases → Draft a new release
2. Tag: v1.3.0
3. Title: Version 1.3.0 - Dark Mode
4. Description: Changelog
5. Publish release

### Через CLI



---

## Шаг 8: Публикация в npm

Login at:
https://www.npmjs.com/login?next=/login/cli/abe5011d-ce33-487e-99f6-03aa9ffe8f9a
Username: 

---

## Шаг 9: Уведомление

- GitHub Discussions пост
- Twitter/Social media
- Email рассылка

---

## Hotfix релиз

v2.0.1

---

## Pre-release

v2.0.2-beta.0

На GitHub отметь "This is a pre-release".

---

## Автоматизация через GitHub Actions

.github/workflows/release.yml:


---

## Checklist



---

## Полная последовательность

v2.1.0

---

## Типичные ошибки

### Забыл push tags



### Неправильное версионирование

Следуй SemVer строго.

### Релиз без тестов

Всегда npm test перед релизом!

---

## Rollback

### GitHub Release

Edit release → Mark as pre-release или Delete

### npm

- package@1.3.0

### Git tag



---

## Заключение

Релиз процесс:

1. **Prepare** - тесты, линтеры, сборка
2. **Version** - SemVer
3. **Changelog** - документация изменений
4. **Tag** - annotated tag
5. **Push** - с тегами
6. **Release** - GitHub Release
7. **Publish** - npm (если библиотека)
8. **Notify** - уведомление пользователей
9. **Automate** - CI/CD

Релиз должен быть предсказуемым и воспроизводимым!
