from __future__ import annotations

import argparse
import csv
import subprocess
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


MANIFEST_HEADER = [
    "экспорт",
    "исходный_размер_мб",
    "копия_jsonl_мб",
    "markdown_мб",
    "html_мб",
    "выводы_инструментов",
    "решение",
]


@dataclass
class SessionChoice:
    thread_id: str
    slug: str
    note: str


def parse_choice(value: str) -> SessionChoice:
    parts = value.split("=", 2)
    if len(parts) < 2:
        raise argparse.ArgumentTypeError("Ожидается формат ID=slug или ID=slug=note")
    thread_id = parts[0].strip()
    slug = parts[1].strip()
    note = parts[2].strip() if len(parts) == 3 else "Пакетный экспорт"
    if not thread_id or not slug:
        raise argparse.ArgumentTypeError("ID и slug не должны быть пустыми")
    return SessionChoice(thread_id=thread_id, slug=slug, note=note)


def mb(path: Path) -> float:
    return round(path.stat().st_size / 1024 / 1024, 2)


def load_index(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return {row["thread_id"]: row for row in csv.DictReader(f)}


def read_manifest(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return {row["экспорт"]: row for row in csv.DictReader(f)}


def write_manifest(path: Path, rows: dict[str, dict[str, str]]) -> None:
    ordered = sorted(rows.values(), key=lambda row: row["экспорт"])
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_HEADER)
        writer.writeheader()
        writer.writerows(ordered)


def run_codlogs(session_jsonl: Path, include_tool_results: bool, include_images: bool) -> None:
    for mode in ("--md", "--html"):
        codlogs = shutil.which("codlogs") or shutil.which("codlogs.cmd")
        cmd = [codlogs or "codlogs", mode, str(session_jsonl)]
        if include_images:
            cmd.append("--include-images")
        if include_tool_results:
            cmd.append("--include-tool-results")
        if codlogs:
            subprocess.run(cmd, check=True)
        else:
            subprocess.run(subprocess.list2cmdline(cmd), shell=True, check=True)


def export_one(
    choice: SessionChoice,
    row: dict[str, str],
    out_root: Path,
    max_size_mb: float,
    allow_huge: bool,
    include_tool_results: bool,
    include_images: bool,
    force: bool,
    dry_run: bool,
) -> dict[str, str] | None:
    source = Path(row["path"])
    source_size = float(row["size_mb"])
    if source_size > max_size_mb and not allow_huge:
        print(f"SKIP huge {choice.slug}: {source_size} MB > limit {max_size_mb} MB")
        return None

    export_dir = out_root / choice.slug
    session_jsonl = export_dir / "session.jsonl"
    session_md = export_dir / "session.md"
    session_html = export_dir / "session.html"

    if session_jsonl.exists() and not force and session_md.exists() and session_html.exists():
        print(f"SKIP exists {choice.slug}: use --force to overwrite")
        return {
            "экспорт": choice.slug,
            "исходный_размер_мб": f"{source_size:.2f}",
            "копия_jsonl_мб": f"{mb(session_jsonl):.2f}",
            "markdown_мб": f"{mb(session_md):.2f}" if session_md.exists() else "0.00",
            "html_мб": f"{mb(session_html):.2f}" if session_html.exists() else "0.00",
            "выводы_инструментов": "да" if include_tool_results else "нет",
            "решение": choice.note,
        }

    if dry_run:
        print(f"DRY {choice.slug}: {source_size:.2f} MB project={row.get('project', '')}")
        return None

    export_dir.mkdir(parents=True, exist_ok=True)
    if force or not session_jsonl.exists():
        shutil.copy2(source, session_jsonl)
    run_codlogs(session_jsonl, include_tool_results=include_tool_results, include_images=include_images)

    result = {
        "экспорт": choice.slug,
        "исходный_размер_мб": f"{source_size:.2f}",
        "копия_jsonl_мб": f"{mb(session_jsonl):.2f}",
        "markdown_мб": f"{mb(session_md):.2f}" if session_md.exists() else "0.00",
        "html_мб": f"{mb(session_html):.2f}" if session_html.exists() else "0.00",
        "выводы_инструментов": "да" if include_tool_results else "нет",
        "решение": choice.note,
    }
    print(
        "EXPORTED "
        f"{choice.slug}: jsonl={result['копия_jsonl_мб']} MB "
        f"md={result['markdown_мб']} MB html={result['html_мб']} MB"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Пакетный приватный экспорт выбранных Codex-сессий через копии JSONL."
    )
    parser.add_argument("--index", type=Path, required=True, help="Путь к sessions-index.csv")
    parser.add_argument("--out", type=Path, required=True, help="Папка docs/codex-session-vault/exports")
    parser.add_argument("--session", action="append", type=parse_choice, default=[], help="ID=slug или ID=slug=note")
    parser.add_argument("--max-size-mb", type=float, default=200.0, help="Лимит обычного экспорта")
    parser.add_argument("--allow-huge", action="store_true", help="Разрешить экспорт сессий больше лимита")
    parser.add_argument("--include-tool-results", action="store_true", help="Включить выводы инструментов")
    parser.add_argument("--include-images", action="store_true", help="Экспортировать изображения")
    parser.add_argument("--force", action="store_true", help="Перезаписать существующие папки экспорта")
    parser.add_argument("--dry-run", action="store_true", help="Только показать, что будет экспортировано")
    args = parser.parse_args()

    if not args.session:
        parser.error("Нужно указать хотя бы один --session ID=slug")

    index = load_index(args.index)
    args.out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / "export-manifest.csv"
    manifest = read_manifest(manifest_path)

    exported = 0
    skipped_missing = 0
    for choice in args.session:
        row = index.get(choice.thread_id)
        if not row:
            print(f"MISSING {choice.thread_id}")
            skipped_missing += 1
            continue
        result = export_one(
            choice=choice,
            row=row,
            out_root=args.out,
            max_size_mb=args.max_size_mb,
            allow_huge=args.allow_huge,
            include_tool_results=args.include_tool_results,
            include_images=args.include_images,
            force=args.force,
            dry_run=args.dry_run,
        )
        if result:
            manifest[choice.slug] = result
            exported += 1

    if not args.dry_run:
        write_manifest(manifest_path, manifest)

    print(
        f"OK exported_or_recorded={exported} missing={skipped_missing} "
        f"manifest={manifest_path} at={datetime.now().isoformat(timespec='seconds')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
