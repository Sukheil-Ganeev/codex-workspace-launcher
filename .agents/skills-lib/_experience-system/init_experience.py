#!/usr/bin/env python3
"""
Скрипт инициализации системы experience/ для скиллов.

Использование:
    python init_experience.py                    # Все скиллы
    python init_experience.py имя-скилла         # Конкретный скилл
    python init_experience.py --list             # Показать все скиллы
"""

import os
import sys
from pathlib import Path
from datetime import date

SKILLS_DIR = Path(r"C:/Users/londo/.claude/skills")

# Скиллы которые пропускаем (системные папки)
SKIP_DIRS = {
    "_experience-system",
    "__pycache__",
    ".git",
}

INDEX_TEMPLATE = '''# Опыт: {skill_name}

> Последнее обновление: {date}

---

## Критические уроки (топ-5)

1. *Пока нет записей*

---

## Статистика

- **Всего записей:** 0
- **Fixes:** 0
- **Improvements:** 0
- **Patterns:** 0
- **Warnings:** 0

---

## Fixes (исправленные ошибки)

| ID | Severity | Описание |
|----|----------|----------|
| — | — | Пока нет записей |

---

## Improvements (улучшения)

| ID | Severity | Описание |
|----|----------|----------|
| — | — | Пока нет записей |

---

## Patterns (паттерны)

| ID | Описание |
|----|----------|
| — | Пока нет записей |

---

## Warnings (что НЕ делать)

| ID | Severity | Описание |
|----|----------|----------|
| — | — | Пока нет записей |

---

## Теги

*Теги появятся по мере накопления опыта*
'''


def get_skill_dirs():
    """Получить список директорий скиллов."""
    skills = []
    for item in SKILLS_DIR.iterdir():
        if item.is_dir() and item.name not in SKIP_DIRS:
            # Проверяем наличие SKILL.md
            skill_file = item / "SKILL.md"
            if skill_file.exists():
                skills.append(item)
    return sorted(skills, key=lambda x: x.name)


def init_experience(skill_dir: Path, force: bool = False):
    """Инициализировать experience/ для скилла."""
    skill_name = skill_dir.name
    exp_dir = skill_dir / "experience"

    # Проверяем существование
    if exp_dir.exists() and not force:
        index_file = exp_dir / "_index.md"
        if index_file.exists():
            print(f"  [SKIP] {skill_name} — experience/ уже существует")
            return False

    # Создаём структуру
    subdirs = ["fixes", "improvements", "patterns", "warnings"]

    exp_dir.mkdir(exist_ok=True)
    for subdir in subdirs:
        (exp_dir / subdir).mkdir(exist_ok=True)

    # Создаём _index.md
    index_content = INDEX_TEMPLATE.format(
        skill_name=skill_name,
        date=date.today().isoformat()
    )

    index_file = exp_dir / "_index.md"
    index_file.write_text(index_content, encoding="utf-8")

    print(f"  [OK] {skill_name} — experience/ создан")
    return True


def main():
    args = sys.argv[1:]

    if "--list" in args:
        # Показать список скиллов
        skills = get_skill_dirs()
        print(f"\nНайдено скиллов: {len(skills)}\n")
        for skill in skills:
            exp_exists = (skill / "experience" / "_index.md").exists()
            status = "[+]" if exp_exists else "[ ]"
            print(f"  {status} {skill.name}")
        print(f"\n[+] = experience/ есть, [ ] = нет\n")
        return

    if args and args[0] != "--force":
        # Конкретный скилл
        skill_name = args[0]
        skill_dir = SKILLS_DIR / skill_name

        if not skill_dir.exists():
            print(f"Ошибка: скилл '{skill_name}' не найден")
            sys.exit(1)

        force = "--force" in args
        print(f"\nИнициализация experience/ для: {skill_name}")
        init_experience(skill_dir, force)
    else:
        # Все скиллы
        force = "--force" in args
        skills = get_skill_dirs()

        print(f"\nИнициализация experience/ для {len(skills)} скиллов:\n")

        created = 0
        skipped = 0

        for skill in skills:
            if init_experience(skill, force):
                created += 1
            else:
                skipped += 1

        print(f"\n--- Итого ---")
        print(f"Создано: {created}")
        print(f"Пропущено: {skipped}")
        print()


if __name__ == "__main__":
    main()
