from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SECTION_RE = re.compile(r"^###\s+(\S+)\s+(.+?)\s*$")
META_RE = re.compile(r"^-\s+([^:]+):\s+`?(.+?)`?\s*$")
WIN_PATH_RE = re.compile(r"[A-Z]:\\[^\n\r\t<>|\"']+")
FILE_RE = re.compile(r"[\wА-Яа-яЁё .()@+-]+\.(?:md|html|csv|json|jsonl|py|ps1|toml|ts|tsx|js|jsx|css|yml|yaml)", re.IGNORECASE)


DECISION_PATTERNS = [
    "решение",
    "вывод",
    "главный вывод",
    "готово",
    "сделал",
    "создал",
    "создан",
    "установил",
    "проверил",
    "лучший формат",
    "по умолчанию",
]


NEXT_PATTERNS = [
    "следующий шаг",
    "next step",
    "что еще не сделано",
    "осталось",
    "нужно сделать",
    "todo",
]


RULE_PATTERNS = [
    "всегда",
    "никогда",
    "нельзя",
    "по умолчанию",
    "лучше",
    "нужно",
    "правило",
    "рекомендуется",
    "не трогать",
    "read-only",
    "ignore",
    ".gitignore",
]


COMMAND_PREFIXES = (
    "python ",
    "node ",
    "npm ",
    "npm.cmd ",
    "npx ",
    "git ",
    "codlogs ",
    "codlogs-sessions ",
    "bun ",
    "powershell ",
    "pwsh ",
)


@dataclass
class Entry:
    timestamp: str
    role: str
    text: str


@dataclass
class DistillRecord:
    slug: str
    session_id: str
    started: str
    cwd: str
    source_md: str
    included_tool_results: str
    user_messages: int
    assistant_messages: int
    tool_sections: int
    goal: str
    key_decisions_count: int
    next_steps_count: int
    files_count: int
    commands_count: int
    summary_file: str


def clean(value: str, limit: int | None = None) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    if limit and len(value) > limit:
        return value[: limit - 1].rstrip() + "..."
    return value


def strip_code_fences(text: str) -> str:
    return text.replace("~~~", "").replace("```", "")


def parse_export(path: Path) -> tuple[dict[str, str], list[Entry]]:
    meta: dict[str, str] = {}
    entries: list[Entry] = []
    current: Entry | None = None

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        meta_match = META_RE.match(raw)
        if meta_match and not entries:
            meta[meta_match.group(1).strip()] = meta_match.group(2).strip("`")
            continue

        section_match = SECTION_RE.match(raw)
        if section_match:
            if current:
                entries.append(current)
            current = Entry(
                timestamp=section_match.group(1),
                role=section_match.group(2).strip(),
                text="",
            )
            continue

        if current:
            current.text += raw + "\n"

    if current:
        entries.append(current)
    return meta, entries


def is_bootstrap(text: str) -> bool:
    lowered = text.lower()
    return "# agents.md instructions" in lowered or "<instructions>" in lowered


def interesting_lines(text: str, patterns: Iterable[str], limit: int = 12) -> list[str]:
    found: list[str] = []
    for line in strip_code_fences(text).splitlines():
        line_clean = clean(line)
        if not line_clean:
            continue
        lowered = line_clean.lower()
        if any(pattern in lowered for pattern in patterns):
            found.append(clean(line_clean, 260))
        if len(found) >= limit:
            break
    return found


def extract_commands(text: str, limit: int = 20) -> list[str]:
    commands: list[str] = []
    for line in strip_code_fences(text).splitlines():
        line_clean = clean(line)
        if not line_clean:
            continue
        lowered = line_clean.lower()
        if lowered.startswith(COMMAND_PREFIXES):
            commands.append(line_clean)
        elif line_clean.startswith("$ ") and len(line_clean) > 2:
            commands.append(line_clean[2:])
        if len(commands) >= limit:
            break
    return commands


def extract_files(text: str, limit: int = 30) -> list[str]:
    files: list[str] = []
    for match in WIN_PATH_RE.findall(text):
        files.append(clean(match, 240))
    for match in FILE_RE.findall(text):
        files.append(clean(match, 160))
    deduped = []
    seen = set()
    for item in files:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(item)
        if len(deduped) >= limit:
            break
    return deduped


def bullet_list(items: list[str], empty: str = "_Не найдено автоматически._") -> str:
    if not items:
        return empty
    return "\n".join(f"- {item}" for item in items)


def distill_one(path: Path, out_dir: Path) -> DistillRecord:
    meta, entries = parse_export(path)
    slug = path.parent.name
    user_entries = [e for e in entries if e.role.startswith("User") and not is_bootstrap(e.text)]
    assistant_entries = [e for e in entries if e.role.startswith("Assistant")]
    tool_entries = [e for e in entries if e.role.startswith("Tool")]
    all_text = "\n".join(e.text for e in entries)
    assistant_text = "\n".join(e.text for e in assistant_entries)

    goal = clean(user_entries[0].text if user_entries else "", 320)
    key_decisions = interesting_lines(assistant_text, DECISION_PATTERNS, 20)
    next_steps = interesting_lines(assistant_text, NEXT_PATTERNS, 20)
    rule_candidates = interesting_lines(assistant_text, RULE_PATTERNS, 25)
    commands = extract_commands(all_text, 30)
    files = extract_files(all_text, 40)

    summary_dir = out_dir / "session-summaries"
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_path = summary_dir / f"{slug}.md"

    report = f"""# Session Distillation: {slug}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Metadata

- Session ID: `{meta.get("Session ID", "")}`
- Started: `{meta.get("Started", "")}`
- CWD: `{meta.get("CWD", "")}`
- Source MD: `{path}`
- Included tool results: `{meta.get("Included tool calls and results", "")}`

## Goal

{goal or "_Не найдено автоматически._"}

## Key Decisions / Outcomes

{bullet_list(key_decisions)}

## Files / Artifacts Mentioned

{bullet_list(files)}

## Commands Mentioned

{bullet_list(commands)}

## Next Steps Found

{bullet_list(next_steps)}

## Candidate Rules / Knowledge To Promote

{bullet_list(rule_candidates)}

## Counts

| Metric | Count |
|---|---:|
| User messages | {len(user_entries)} |
| Assistant messages | {len(assistant_entries)} |
| Tool sections | {len(tool_entries)} |
| Decisions found | {len(key_decisions)} |
| Next steps found | {len(next_steps)} |
| File refs found | {len(files)} |
| Commands found | {len(commands)} |
"""
    summary_path.write_text(report, encoding="utf-8")

    return DistillRecord(
        slug=slug,
        session_id=meta.get("Session ID", ""),
        started=meta.get("Started", ""),
        cwd=meta.get("CWD", ""),
        source_md=str(path),
        included_tool_results=meta.get("Included tool calls and results", ""),
        user_messages=len(user_entries),
        assistant_messages=len(assistant_entries),
        tool_sections=len(tool_entries),
        goal=goal,
        key_decisions_count=len(key_decisions),
        next_steps_count=len(next_steps),
        files_count=len(files),
        commands_count=len(commands),
        summary_file=str(summary_path),
    )


def write_csv(path: Path, records: list[DistillRecord]) -> None:
    fieldnames = list(DistillRecord.__annotations__.keys())
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def write_overview(out_dir: Path, records: list[DistillRecord]) -> None:
    by_tool_results = Counter(r.included_tool_results for r in records)
    total_decisions = sum(r.key_decisions_count for r in records)
    total_next = sum(r.next_steps_count for r in records)
    total_files = sum(r.files_count for r in records)
    total_commands = sum(r.commands_count for r in records)

    rows = "\n".join(
        f"| {r.slug} | {r.user_messages} | {r.assistant_messages} | {r.key_decisions_count} | {r.next_steps_count} | `{r.summary_file}` |"
        for r in records
    )
    report = f"""# Выжимка знаний из Codex-сессий

Дата: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Резюме

- Обработано экспортов: **{len(records)}**
- Найдено решений/выводов: **{total_decisions}**
- Найдено следующих шагов: **{total_next}**
- Найдено ссылок на файлы: **{total_files}**
- Найдено команд: **{total_commands}**

## По типу экспорта

| Выводы инструментов включены | Сессий |
|---|---:|
"""
    for key, count in by_tool_results.most_common():
        report += f"| {key or 'unknown'} | {count} |\n"

    report += f"""
## Сессии

| Экспорт | Сообщений пользователя | Сообщений ассистента | Решений | Следующих шагов | Выжимка |
|---|---:|---:|---:|---:|---|
{rows}

## Решение по формату

Эта версия distiller работает как первый автоматический слой: она не заменяет человеческую/LLM-выжимку, но быстро находит цели, решения, команды, файлы и кандидаты в правила.

Для рабочего Vault нужен следующий слой: LLM-проверка каждой выжимки, чтобы аккуратно выбрать, что переносить в `AGENTS.md`, глобальную память или отдельные навыки.
"""
    (out_dir / "README.md").write_text(report, encoding="utf-8")


def write_promotion_candidates(out_dir: Path) -> None:
    summary_files = sorted((out_dir / "session-summaries").glob("*.md"))
    blocks: list[str] = []
    for summary in summary_files:
        text = summary.read_text(encoding="utf-8", errors="replace")
        capture = False
        items: list[str] = []
        for line in text.splitlines():
            if line.startswith("## Candidate Rules"):
                capture = True
                continue
            if capture and line.startswith("## "):
                break
            if capture and line.startswith("- "):
                items.append(line)
        if items:
            blocks.append(f"## {summary.stem}\n\n" + "\n".join(items))

    output = "# Кандидаты на перенос\n\n"
    output += "Кандидаты ниже нужно проверять вручную перед переносом в `AGENTS.md`, память или навыки.\n\n"
    output += "\n\n".join(blocks) if blocks else "_Кандидаты не найдены автоматически._\n"
    (out_dir / "promotion-candidates.md").write_text(output, encoding="utf-8")


def write_safe_review(out_dir: Path, records: list[DistillRecord]) -> None:
    report = f"""# Проверка выжимки знаний

Дата: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Что проверено

Первый `knowledge-distiller` обработал Markdown-экспорты `codlogs` и создал приватные выжимки по отдельным сессиям.

## Решение по приватности

Детальные файлы с целями, кандидатами в правила и фрагментами из стенограмм считаются приватными и игнорируются git:

- `session-summaries/*`
- `distillation-index.csv`
- `distillation-index.json`
- `promotion-candidates.md`

Публично безопасный слой:

- `README.md`
- `knowledge-review.md`
- `.gitignore`

## Что distiller умеет сейчас

- берет `session.md` из экспортов Vault;
- пропускает экспорты с выводами инструментов, если это не включено явно;
- находит цель сессии;
- считает сообщения;
- вытаскивает решения/выводы;
- вытаскивает следующие шаги;
- вытаскивает команды и ссылки на файлы;
- формирует кандидатов на перенос в `AGENTS.md`, память или навыки.

## Что distiller пока делает грубо

- эвристики могут вытаскивать слишком длинные или слишком личные фразы;
- он не понимает контекст так глубоко, как LLM-проверка;
- кандидаты в правила нельзя переносить автоматически;
- политические, личные, токены, браузерные сессии и бизнес-детали требуют ручной чистки.

## Проверенные экспорты

| Экспорт | Сообщений пользователя | Сообщений ассистента | Решений | Следующих шагов | Выводы инструментов |
|---|---:|---:|---:|---:|---|
"""
    for record in records:
        report += (
            f"| {record.slug} | {record.user_messages} | {record.assistant_messages} | "
            f"{record.key_decisions_count} | {record.next_steps_count} | {record.included_tool_results or 'unknown'} |\n"
        )

    report += """
## Чистые правила, которые уже можно закрепить

1. Оригинальные `C:\\Users\\londo\\.codex\\sessions` не менять: только читать.
2. Для `codlogs` сначала копировать `session.jsonl` в папку экспорта Vault, потом экспортировать копию.
3. По умолчанию делать `session.md` и `session.html` без `--include-tool-results`.
4. `--include-tool-results` использовать только для расследований.
5. Любые выжимки, полученные из стенограмм, считать приватными, пока они не прошли ручную чистку.
6. Кандидаты в `AGENTS.md`, память и навыки переносить только после проверки владельцем.

## Следующий шаг

Сделать LLM-проверку: взять приватный `promotion-candidates.md`, очистить его от личного и шумного, затем сформировать 3 списка:

- правила для `AGENTS.md`;
- правила для пользовательской памяти;
- идеи для новых или улучшенных навыков.
"""
    (out_dir / "knowledge-review.md").write_text(report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Сжать Markdown-экспорты codlogs в короткие выжимки знаний.")
    parser.add_argument("--exports-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--include-tool-result-exports", action="store_true")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    records: list[DistillRecord] = []
    for path in sorted(args.exports_root.rglob("session.md")):
        meta, _ = parse_export(path)
        if meta.get("Included tool calls and results", "").lower() == "yes" and not args.include_tool_result_exports:
            continue
        records.append(distill_one(path, args.out))

    write_csv(args.out / "distillation-index.csv", records)
    (args.out / "distillation-index.json").write_text(
        json.dumps([asdict(r) for r in records], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_overview(args.out, records)
    write_promotion_candidates(args.out)
    write_safe_review(args.out, records)
    print(f"OK distilled={len(records)} out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
