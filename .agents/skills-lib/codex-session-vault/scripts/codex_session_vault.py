from __future__ import annotations

import argparse
import csv
import html
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


UUID_RE = re.compile(
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    re.IGNORECASE,
)


@dataclass
class SessionRecord:
    thread_id: str
    title: str
    path: str
    size_bytes: int
    size_mb: float
    modified_at: str
    date_bucket: str
    year_month: str
    cwd: str
    project: str
    model: str
    source: str
    first_user_message: str
    risk_size: str
    parse_status: str


def iso_from_timestamp(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def safe_text(value: str, limit: int = 180) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "..."


def thread_id_from_path(path: Path) -> str:
    match = UUID_RE.search(path.name)
    return match.group(1) if match else ""


def date_from_path(path: Path) -> tuple[str, str]:
    parts = path.parts
    for i in range(len(parts) - 2):
        if (
            re.fullmatch(r"20\d{2}", parts[i])
            and re.fullmatch(r"\d{2}", parts[i + 1])
            and re.fullmatch(r"\d{2}", parts[i + 2])
        ):
            date_bucket = f"{parts[i]}-{parts[i + 1]}-{parts[i + 2]}"
            return date_bucket, date_bucket[:7]
    match = re.search(r"(20\d{2})-(\d{2})-(\d{2})", path.name)
    if match:
        date_bucket = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        return date_bucket, date_bucket[:7]
    return "unknown", "unknown"


def size_bucket(size_bytes: int) -> str:
    mb = size_bytes / 1024 / 1024
    if mb >= 250:
        return "huge_250mb_plus"
    if mb >= 50:
        return "large_50mb_plus"
    if mb >= 10:
        return "medium_10mb_plus"
    return "small_under_10mb"


def risk_label(risk_size: str) -> str:
    labels = {
        "huge_250mb_plus": "очень большая, 250 МБ+",
        "large_50mb_plus": "большая, 50 МБ+",
        "medium_10mb_plus": "средняя, 10 МБ+",
        "small_under_10mb": "маленькая, до 10 МБ",
    }
    return labels.get(risk_size, risk_size)


def display_title(record: "SessionRecord") -> str:
    return record.title.strip() or "Без названия"


def project_from_cwd(cwd: str) -> str:
    if not cwd:
        return "unknown"
    normalized = cwd.replace("\\", "/").rstrip("/")
    return normalized.split("/")[-1] or normalized


def load_titles(index_path: Path) -> dict[str, str]:
    titles: dict[str, str] = {}
    if not index_path.exists():
        return titles
    with index_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            thread_id = str(row.get("id") or "")
            title = str(row.get("thread_name") or "").strip()
            if thread_id and title:
                titles[thread_id] = title
    return titles


def payload_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, list):
        chunks: list[str] = []
        for item in payload:
            if isinstance(item, dict):
                chunks.append(str(item.get("text") or item.get("content") or ""))
            else:
                chunks.append(str(item))
        return " ".join(chunks)
    if isinstance(payload, dict):
        return str(payload.get("text") or payload.get("content") or "")
    return ""


def inspect_head(path: Path, max_lines: int, max_bytes: int) -> dict[str, str]:
    result = {
        "cwd": "",
        "model": "",
        "source": "",
        "first_user_message": "",
        "parse_status": "ok",
    }
    read_bytes = 0
    lines_seen = 0
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                read_bytes += len(line.encode("utf-8", errors="ignore"))
                lines_seen += 1
                if read_bytes > max_bytes or lines_seen > max_lines:
                    break
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    result["parse_status"] = "head_json_error"
                    continue

                row_type = row.get("type")
                payload = row.get("payload", {})
                if row_type == "session_meta" and isinstance(payload, dict):
                    result["cwd"] = str(payload.get("cwd") or result["cwd"])
                    result["model"] = str(payload.get("model") or result["model"])
                    result["source"] = str(payload.get("source") or result["source"])

                if not result["first_user_message"]:
                    if row_type == "event_msg" and isinstance(payload, dict):
                        if payload.get("type") == "user_message":
                            result["first_user_message"] = safe_text(payload_text(payload.get("message")))
                    elif row_type == "response_item" and isinstance(payload, dict):
                        if payload.get("type") == "message" and payload.get("role") == "user":
                            result["first_user_message"] = safe_text(payload_text(payload.get("content")))
    except OSError as exc:
        result["parse_status"] = f"os_error:{exc.__class__.__name__}"
    return result


def audit_sessions(codex_home: Path, out_dir: Path, max_head_lines: int, max_head_bytes: int) -> list[SessionRecord]:
    sessions_dir = codex_home / "sessions"
    index_path = codex_home / "session_index.jsonl"
    titles = load_titles(index_path)
    records: list[SessionRecord] = []

    for path in sorted(sessions_dir.rglob("*.jsonl")):
        stat = path.stat()
        thread_id = thread_id_from_path(path)
        date_bucket, year_month = date_from_path(path)
        head = inspect_head(path, max_head_lines, max_head_bytes)
        cwd = head["cwd"]
        records.append(
            SessionRecord(
                thread_id=thread_id,
                title=titles.get(thread_id, ""),
                path=str(path),
                size_bytes=stat.st_size,
                size_mb=round(stat.st_size / 1024 / 1024, 2),
                modified_at=iso_from_timestamp(stat.st_mtime),
                date_bucket=date_bucket,
                year_month=year_month,
                cwd=cwd,
                project=project_from_cwd(cwd),
                model=head["model"],
                source=head["source"],
                first_user_message=head["first_user_message"],
                risk_size=size_bucket(stat.st_size),
                parse_status=head["parse_status"],
            )
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    write_outputs(out_dir, codex_home, records)
    return records


def write_csv(path: Path, records: list[SessionRecord]) -> None:
    fieldnames = list(asdict(records[0]).keys()) if records else list(SessionRecord.__annotations__.keys())
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def md_table(rows: list[tuple[str, Any]], headers: tuple[str, str], limit: int = 20) -> str:
    out = [f"| {headers[0]} | {headers[1]} |", "|---|---:|"]
    for key, value in rows[:limit]:
        out.append(f"| {key} | {value} |")
    return "\n".join(out)


def html_table(records: list[SessionRecord], limit: int = 100) -> str:
    headers = ["Дата", "Название", "Проект", "Размер, МБ", "Категория"]
    rows = ["<table>", "<thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead>", "<tbody>"]
    for record in records[:limit]:
        values = [
            record.date_bucket,
            display_title(record),
            record.project,
            f"{record.size_mb:.2f}",
            risk_label(record.risk_size),
        ]
        rows.append("<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in values) + "</tr>")
    rows.append("</tbody></table>")
    return "\n".join(rows)


def write_outputs(out_dir: Path, codex_home: Path, records: list[SessionRecord]) -> None:
    records_by_size = sorted(records, key=lambda r: r.size_bytes, reverse=True)
    total_size = sum(r.size_bytes for r in records)
    by_month = Counter(r.year_month for r in records)
    by_date = Counter(r.date_bucket for r in records)
    by_project = Counter(r.project for r in records)
    by_size = Counter(r.risk_size for r in records)
    by_parse = Counter(r.parse_status for r in records)

    write_csv(out_dir / "sessions-index.csv", records_by_size)
    (out_dir / "sessions-index.json").write_text(
        json.dumps([asdict(r) for r in records_by_size], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "codex_home": str(codex_home),
        "session_count": len(records),
        "total_size_bytes": total_size,
        "total_size_gb": round(total_size / 1024 / 1024 / 1024, 2),
        "largest_session_mb": records_by_size[0].size_mb if records_by_size else 0,
        "size_buckets": by_size.most_common(),
        "parse_status": by_parse.most_common(),
        "top_months": by_month.most_common(20),
        "top_dates": by_date.most_common(20),
        "top_projects": by_project.most_common(30),
    }
    (out_dir / "vault-audit-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report = f"""# Аудит Codex Session Vault

Дата: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Резюме

- Источник: локальная папка Codex-сессий.
- Сессий найдено: **{len(records)}**
- Общий размер: **{summary["total_size_gb"]} ГБ**
- Самая большая сессия: **{summary["largest_session_mb"]} МБ**
- Исходные сессии не изменялись: аудит только для чтения.

## Размеры

{md_table(by_size.most_common(), ("Категория", "Сессий"))}

## Активность по месяцам

{md_table(by_month.most_common(20), ("Месяц", "Сессий"))}

## Самые активные дни

{md_table(by_date.most_common(20), ("Дата", "Сессий"))}

## Проекты / рабочие папки

{md_table(by_project.most_common(30), ("Проект", "Сессий"))}

## Самые большие сессии

| Размер, МБ | Дата | Проект | Название |
|---:|---|---|---|
"""
    for record in records_by_size[:20]:
        report += (
            f"| {record.size_mb:.2f} | {record.date_bucket} | {record.project} | "
            f"{display_title(record)} |\n"
        )

    report += """
## Что это значит

1. Архив уже большой, поэтому нельзя делать наивный полный импорт всех стенограмм в память.
2. Нужен двухслойный подход: быстрый индекс всех сессий плюс глубокий экспорт только выбранных сессий.
3. Большие сессии сначала лучше санитайзить/сжимать, а не открывать целиком.
4. Полные стенограммы лучше не коммитить в git: там могут быть приватные данные, токены, пути и бизнес-контекст.

## Следующий шаг

1. Установить/проверить `codlogs` как движок экспорта одной Codex-сессии в Markdown/HTML.
2. Выбрать 10-20 самых важных сессий и сделать глубокий экспорт.
3. Сделать `knowledge-distiller`: выжимать из экспортов правила, решения, команды и следующие шаги.
"""
    (out_dir / "README.md").write_text(report, encoding="utf-8")

    html_doc = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>Аудит Codex Session Vault</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 0; background: #f6f7f9; color: #15171a; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 32px 20px 60px; }}
    h1 {{ font-size: 32px; margin: 0 0 8px; }}
    .muted {{ color: #626975; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 24px 0; }}
    .metric {{ background: white; border: 1px solid #dde1e7; border-radius: 8px; padding: 16px; }}
    .metric b {{ display: block; font-size: 24px; margin-top: 8px; }}
    section {{ background: white; border: 1px solid #dde1e7; border-radius: 8px; padding: 18px; margin-top: 16px; overflow: auto; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #e6e9ef; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f0f2f5; position: sticky; top: 0; }}
    code {{ white-space: normal; word-break: break-all; }}
    @media (max-width: 820px) {{ .grid {{ grid-template-columns: 1fr 1fr; }} }}
  </style>
</head>
<body>
<main>
  <h1>Аудит Codex Session Vault</h1>
  <p class="muted">Индекс локальных Codex-сессий только для чтения. Сырые пути и фрагменты сообщений скрыты.</p>
  <div class="grid">
    <div class="metric">Сессий<b>{len(records)}</b></div>
    <div class="metric">Общий размер<b>{summary["total_size_gb"]} ГБ</b></div>
    <div class="metric">Самая большая<b>{summary["largest_session_mb"]} МБ</b></div>
    <div class="metric">Крупных 250 МБ+<b>{by_size.get("huge_250mb_plus", 0)}</b></div>
  </div>
  <section><h2>Самые большие сессии</h2>{html_table(records_by_size, 100)}</section>
</main>
</body>
</html>
"""
    (out_dir / "dashboard.html").write_text(html_doc, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Аудит локального архива Codex-сессий только для чтения.")
    parser.add_argument("--codex-home", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-head-lines", type=int, default=80)
    parser.add_argument("--max-head-bytes", type=int, default=1_000_000)
    args = parser.parse_args()

    records = audit_sessions(args.codex_home, args.out, args.max_head_lines, args.max_head_bytes)
    total_gb = sum(r.size_bytes for r in records) / 1024 / 1024 / 1024
    print(f"OK sessions={len(records)} size_gb={total_gb:.2f} out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
