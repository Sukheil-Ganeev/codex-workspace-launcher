#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Версионирование и сравнение чатов.
Создаёт копии, отслеживает изменения.
"""

import argparse
import difflib
import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))
from config import CHATS_DIR, HISTORY_DIR, CONTACT_TYPES, ensure_directories

# ═══════════════════════════════════════════════════════════════
# ВЕРСИОНИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════

def get_file_hash(file_path: Path) -> str:
    """Получить хеш файла."""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def create_version(file_path: Path, version_dir: Path = None) -> Path:
    """
    Создать версию файла.

    Returns:
        Путь к созданной версии
    """
    file_path = Path(file_path)

    if version_dir is None:
        version_dir = HISTORY_DIR / file_path.stem

    version_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_hash = get_file_hash(file_path)

    version_name = f"{file_path.stem}_{timestamp}_{file_hash}{file_path.suffix}"
    version_path = version_dir / version_name

    shutil.copy2(file_path, version_path)

    return version_path


def list_versions(file_path: Path) -> List[Dict]:
    """Получить список версий файла."""
    file_path = Path(file_path)
    version_dir = HISTORY_DIR / file_path.stem

    if not version_dir.exists():
        return []

    versions = []
    for vfile in sorted(version_dir.glob(f"{file_path.stem}_*{file_path.suffix}")):
        # Парсим имя: name_YYYYMMDD_HHMMSS_hash.ext
        parts = vfile.stem.split('_')
        if len(parts) >= 4:
            date_str = parts[-3]
            time_str = parts[-2]
            file_hash = parts[-1]

            try:
                version_date = datetime.strptime(f"{date_str}_{time_str}", '%Y%m%d_%H%M%S')
            except ValueError:
                version_date = datetime.fromtimestamp(vfile.stat().st_mtime)

            versions.append({
                'path': str(vfile),
                'filename': vfile.name,
                'date': version_date,
                'hash': file_hash,
                'size': vfile.stat().st_size,
            })

    return sorted(versions, key=lambda x: x['date'], reverse=True)


def get_latest_version(file_path: Path) -> Optional[Path]:
    """Получить последнюю версию файла."""
    versions = list_versions(file_path)
    if versions:
        return Path(versions[0]['path'])
    return None


# ═══════════════════════════════════════════════════════════════
# СРАВНЕНИЕ
# ═══════════════════════════════════════════════════════════════

def diff_files(file1: Path, file2: Path, context_lines: int = 3) -> str:
    """
    Сравнить два файла.

    Returns:
        Унифицированный diff
    """
    with open(file1, 'r', encoding='utf-8') as f:
        lines1 = f.readlines()

    with open(file2, 'r', encoding='utf-8') as f:
        lines2 = f.readlines()

    diff = difflib.unified_diff(
        lines1, lines2,
        fromfile=str(file1),
        tofile=str(file2),
        lineterm='',
        n=context_lines
    )

    return '\n'.join(diff)


def diff_with_latest(file_path: Path) -> Optional[str]:
    """Сравнить файл с последней версией."""
    latest = get_latest_version(file_path)
    if latest:
        return diff_files(latest, file_path)
    return None


def get_changes_summary(diff_text: str) -> Dict:
    """Получить сводку изменений."""
    added = 0
    removed = 0
    modified = 0

    for line in diff_text.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            added += 1
        elif line.startswith('-') and not line.startswith('---'):
            removed += 1

    return {
        'added_lines': added,
        'removed_lines': removed,
        'total_changes': added + removed,
    }


# ═══════════════════════════════════════════════════════════════
# АВТОВЕРСИОНИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════

def auto_version_all_chats() -> List[Path]:
    """Создать версии всех изменённых чатов."""
    versioned = []

    for contact_type in CONTACT_TYPES:
        type_dir = CHATS_DIR / contact_type
        if type_dir.exists():
            for file_path in type_dir.glob("*.md"):
                latest = get_latest_version(file_path)

                # Проверяем нужно ли создавать версию
                if latest is None:
                    # Первая версия
                    version_path = create_version(file_path)
                    versioned.append(version_path)
                else:
                    # Сравниваем хеши
                    current_hash = get_file_hash(file_path)
                    latest_hash = get_file_hash(latest)

                    if current_hash != latest_hash:
                        version_path = create_version(file_path)
                        versioned.append(version_path)

    return versioned


def cleanup_old_versions(keep_last: int = 10):
    """Удалить старые версии, оставить последние N."""
    for version_dir in HISTORY_DIR.iterdir():
        if version_dir.is_dir():
            versions = sorted(version_dir.glob("*.md"),
                            key=lambda x: x.stat().st_mtime, reverse=True)

            for old_version in versions[keep_last:]:
                old_version.unlink()
                print(f"  Удалено: {old_version.name}")


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ ОТЧЁТА
# ═══════════════════════════════════════════════════════════════

def generate_history_report() -> str:
    """Сгенерировать отчёт по истории версий."""
    report = f"""# История версий чатов

*Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}*

---

"""

    for contact_type in CONTACT_TYPES:
        type_dir = CHATS_DIR / contact_type
        if type_dir.exists():
            files = list(type_dir.glob("*.md"))
            if files:
                report += f"## {contact_type.title()}\n\n"

                for file_path in files:
                    versions = list_versions(file_path)
                    report += f"### {file_path.name}\n\n"

                    if versions:
                        report += "| Версия | Дата | Размер |\n"
                        report += "|--------|------|--------|\n"

                        for v in versions[:5]:
                            date_str = v['date'].strftime('%d.%m.%Y %H:%M')
                            size_kb = v['size'] / 1024
                            report += f"| {v['hash']} | {date_str} | {size_kb:.1f} KB |\n"

                        if len(versions) > 5:
                            report += f"\n*... и ещё {len(versions) - 5} версий*\n"
                    else:
                        report += "*Версий нет*\n"

                    report += "\n"

    return report


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Версионирование и сравнение чатов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python diff_chats.py chat.md --version          # Создать версию
  python diff_chats.py chat.md --diff             # Сравнить с последней
  python diff_chats.py chat.md --history          # Показать историю
  python diff_chats.py --auto-version             # Версии всех изменённых
  python diff_chats.py --cleanup --keep 10        # Очистка старых
  python diff_chats.py file1.md file2.md          # Сравнить два файла
        """
    )

    parser.add_argument('files', nargs='*', help='Файл(ы) для обработки')
    parser.add_argument('--version', action='store_true', help='Создать версию')
    parser.add_argument('--diff', action='store_true', help='Сравнить с последней версией')
    parser.add_argument('--history', action='store_true', help='Показать историю')
    parser.add_argument('--auto-version', action='store_true', help='Версии всех изменённых')
    parser.add_argument('--cleanup', action='store_true', help='Очистка старых версий')
    parser.add_argument('--keep', type=int, default=10, help='Сколько версий хранить')
    parser.add_argument('--report', action='store_true', help='Отчёт по истории')

    args = parser.parse_args()

    ensure_directories()

    if args.auto_version:
        versioned = auto_version_all_chats()
        print(f"✓ Создано версий: {len(versioned)}")
        for v in versioned:
            print(f"  {v.name}")
        return

    if args.cleanup:
        print(f"Очистка версий (оставить последние {args.keep})...")
        cleanup_old_versions(args.keep)
        print("✓ Готово")
        return

    if args.report:
        report = generate_history_report()
        print(report)
        return

    if not args.files:
        parser.print_help()
        return

    file_path = Path(args.files[0])

    if len(args.files) == 2:
        # Сравнение двух файлов
        diff_text = diff_files(Path(args.files[0]), Path(args.files[1]))
        print(diff_text)
        summary = get_changes_summary(diff_text)
        print(f"\n--- Сводка: +{summary['added_lines']} -{summary['removed_lines']} ---")
        return

    if args.version:
        version_path = create_version(file_path)
        print(f"✓ Создана версия: {version_path}")
        return

    if args.diff:
        diff_text = diff_with_latest(file_path)
        if diff_text:
            print(diff_text)
            summary = get_changes_summary(diff_text)
            print(f"\n--- Сводка: +{summary['added_lines']} -{summary['removed_lines']} ---")
        else:
            print("Версий для сравнения нет")
        return

    if args.history:
        versions = list_versions(file_path)
        if versions:
            print(f"\nИстория версий: {file_path.name}\n")
            for v in versions:
                date_str = v['date'].strftime('%d.%m.%Y %H:%M')
                size_kb = v['size'] / 1024
                print(f"  [{v['hash']}] {date_str}  {size_kb:.1f} KB")
        else:
            print("Версий нет")
        return

    # По умолчанию - создать версию
    version_path = create_version(file_path)
    print(f"✓ Создана версия: {version_path}")


if __name__ == "__main__":
    main()
