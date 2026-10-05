# Git/GitHub — Полный справочник

Универсальный справочник по Git и GitHub от установки до продвинутых тем. Специально адаптирован для Windows + Git Bash.

## Структура

```
git-github-справочник/
├── SKILL.md                     # 📘 Основное руководство (~4500 слов, 9 модулей)
├── README.md                    # 📍 Этот файл — навигация
├── marketplace.json             # ⚙️ Метаданные скилла
├── assets/
│   ├── templates/               # 📝 Шаблоны (.gitignore, commit/PR/issue)
│   ├── examples/                # 💡 Workflows и примеры
│   └── diagrams/                # 📊 ASCII диаграммы
├── references/                  # 📚 Справочники
│   ├── git-commands-cheatsheet.md        # ⚡ Все команды Git
│   ├── github-workflows.md               # 🤖 GitHub Actions примеры
│   ├── ssh-setup-windows.md              # 🔑 SSH ключи для Windows
│   ├── pat-authentication.md             # 🔐 Personal Access Token
│   ├── troubleshooting.md                # 🔧 Решение 20+ ошибок
│   ├── faq.md                            # ❓ Часто задаваемые вопросы
│   └── glossary.md                       # 📖 Словарь терминов (рус/англ)
├── scripts/                     # 🤖 Скрипты автоматизации
│   ├── convert-windows-path.sh  # 🪟 D:\ → /d/
│   ├── init-repo-helper.sh
│   ├── sync-fork.sh
│   └── cleanup-branches.sh
└── experience/                  # 📖 Накопленный опыт
    └── _index.md                # 🎯 Критические уроки
```

## Quick Start

### Для новичков
1. **SKILL.md** → Модуль 0: Установка и настройка (Windows + Git Bash)
2. **SKILL.md** → Модуль 1: Git Basics (commit, push, pull)
3. **references/git-commands-cheatsheet.md** — шпаргалка команд

### Для опытных
1. **SKILL.md** → Модули 3-8 (Branches, Collaboration, GitHub Actions, Advanced)
2. **references/github-workflows.md** — готовые CI/CD примеры
3. **assets/examples/** — полные workflows

### При проблемах
1. **references/troubleshooting.md** — 20+ типичных ошибок
   - Authentication failed → pat-authentication.md
   - Merge conflicts → conflict-resolution-example.md
   - Windows paths → convert-windows-path.sh
2. **references/faq.md** — ответы на частые вопросы
3. **experience/_index.md** — уроки из реального опыта

## Модули SKILL.md

**Модуль 0:** Установка и настройка (Windows + Git Bash)
**Модуль 1:** Git Basics — commit, push, pull, status
**Модуль 2:** GitHub Integration — PAT, SSH, remote, push/pull
**Модуль 3:** Branches — создание, merge, rebase, конфликты
**Модуль 4:** Collaboration — fork, PRs, code review, issues
**Модуль 5:** GitHub Actions — CI/CD автоматизация
**Модуль 6:** Deployment — GitHub Pages, Netlify, Vercel
**Модуль 7:** .gitignore — игнорирование файлов
**Модуль 8:** Advanced Topics — stash, tags, bisect

## Триггеры активации

Используй этот скилл когда:
- "git", "github"
- "commit", "push", "pull"
- "branch", "merge", "rebase"
- "pull request", "PR"
- "authentication failed"
- "конвертация пути windows"
- "git bash"

## Специфика Windows

✅ **Конвертация путей:** `D:\Downloads\` → `/d/Downloads/`
✅ **Git Bash:** Все команды адаптированы для Git Bash
✅ **SSH ключи:** Настройка для Windows (references/ssh-setup-windows.md)
✅ **Personal Access Token:** Решение проблемы Authentication failed

## Бизнес-кейсы

✅ **Деплой проектов** — интеграция с Netlify, Vercel, GitHub Pages
✅ **Командная работа** — branches, PRs, code review
✅ **Автоматизация** — GitHub Actions для CI/CD
✅ **Версионный контроль** — управление изменениями в коде

## Первый шаг

**Прочитай:** `experience/_index.md` — критические уроки из реального опыта

---

Создано: 2026-02-04
Версия: 1.0.0
Автор: Claude Code + Сухейль
