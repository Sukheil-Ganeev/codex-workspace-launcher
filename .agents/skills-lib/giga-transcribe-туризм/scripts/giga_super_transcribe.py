#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Giga Super Transcribe

Единый скрипт для:
1) транскрибации аудио/видео через GigaAM (основной движок)
2) OCR по кадрам видео через существующий PowerShell-скрипт ocr_extract.ps1

Рекомендуемый запуск (Windows):
D:\Downloads\_SYSTEM\Tools_And_Runtime\_gigaam_venv\Scripts\python.exe giga_super_transcribe.py --inputs <file1> <file2> --ocr
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List


# Готовые коррекции из ваших рабочих скриптов
TOURISM_CORRECTIONS = {
    "сбер банк": "Сбербанк",
    "тинькоф": "Тинькофф",
    "тиньков": "Тинькофф",
    "эмирейтс нбд": "Emirates NBD",
    "марсель": "Марсель",
    "сухейль": "Сухейль",
    "суухейль": "Сухейль",
    "гульназ": "Гульназ",
    "ахмед": "Ахмед",
    "аед": "AED",
    "ибан": "IBAN",
    "айбан": "IBAN",
    "свифт": "SWIFT",
    "абу даби": "Абу-Даби",
    "дубай": "Дубай",
    "burj halifa": "Burj Khalifa",
    "burj khalifa": "Burj Khalifa",
    "dubai marina": "Dubai Marina",
    "yas marina": "Yas Marina",
}

OCR_SCRIPT_DEFAULT = Path(
    r"D:\Downloads\10_PROJECTS\Projects\PROJECT__UNASSIGNED_ROOT_FILES\inbox\07_Code_Config\ocr_extract.ps1"
)


@dataclass
class Segment:
    start_sec: float
    end_sec: float
    text: str


@dataclass
class FileResult:
    input: str
    source_file: str
    transcript_file: str
    transcript_vtt_file: str
    segments_file: str
    ocr_file: str | None
    ocr_json_file: str | None
    duration_sec: float
    segments_count: int
    language: str
    status: str
    error: str | None


def safe_stem(name: str) -> str:
    stem = Path(name).stem
    stem = re.sub(r"[^\w\-. ]+", "_", stem, flags=re.UNICODE)
    stem = stem.strip(" ._")
    return stem or "output"


def format_vtt_timestamp(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    hours = ms // 3_600_000
    ms -= hours * 3_600_000
    minutes = ms // 60_000
    ms -= minutes * 60_000
    secs = ms // 1000
    ms -= secs * 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"


def load_custom_terms(path: Path | None) -> dict[str, str]:
    if not path:
        return {}
    if not path.exists():
        raise FileNotFoundError(f"Файл с терминами не найден: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Файл терминов должен быть JSON-объектом вида {\"как услышал\": \"как надо\"}")
    fixed: dict[str, str] = {}
    for k, v in data.items():
        if isinstance(k, str) and isinstance(v, str) and k.strip() and v.strip():
            fixed[k] = v
    return fixed


def collect_inputs(raw_inputs: List[str], recursive: bool) -> List[str]:
    collected: List[str] = []
    for item in raw_inputs:
        if is_url(item):
            collected.append(item)
            continue

        p = Path(item)
        if p.is_file():
            collected.append(str(p))
            continue

        if p.is_dir():
            pattern = "**/*" if recursive else "*"
            for f in p.glob(pattern):
                if f.is_file() and f.suffix.lower() in {
                    ".mp3", ".wav", ".ogg", ".opus", ".m4a", ".aac", ".flac",
                    ".mp4", ".mov", ".mkv", ".avi", ".m4v", ".webm",
                }:
                    collected.append(str(f))
            continue

        wildcard_matches = list(Path().glob(item))
        if wildcard_matches:
            for f in wildcard_matches:
                if f.is_file():
                    collected.append(str(f))
            continue

        raise FileNotFoundError(f"Вход не найден: {item}")

    deduped: List[str] = []
    seen = set()
    for x in collected:
        key = x.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(x)
    return deduped


def run_cmd(cmd: List[str], fail_message: str) -> str:
    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return (proc.stdout or "").strip()
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        stdout = (e.stdout or "").strip()
        details = stderr or stdout or str(e)
        raise RuntimeError(f"{fail_message}: {details}") from e


def ensure_ffmpeg_tools() -> None:
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError(
            "Не найден ffmpeg/ffprobe в PATH. Установите ffmpeg и повторите запуск."
        )


def is_url(value: str) -> bool:
    return bool(re.match(r"^https?://", value, flags=re.IGNORECASE))


def resolve_input(item: str, work_dir: Path) -> Path:
    """Поддерживает локальный путь и URL."""
    if not is_url(item):
        p = Path(item)
        if not p.exists():
            raise FileNotFoundError(f"Файл не найден: {item}")
        return p

    # Скачивание URL через ffmpeg
    file_name = safe_stem(item) + ".mp4"
    out_path = work_dir / file_name
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        item,
        "-c",
        "copy",
        str(out_path),
    ]
    run_cmd(cmd, f"Не удалось скачать видео по URL {item}")
    return out_path


def media_duration_sec(media_path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(media_path),
    ]
    out = run_cmd(cmd, f"Не удалось получить длительность {media_path.name}")
    try:
        return float(out)
    except ValueError as e:
        raise RuntimeError(f"Некорректная длительность от ffprobe: {out}") from e


def convert_to_wav16k(media_path: Path, wav_path: Path) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(media_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-sample_fmt",
        "s16",
        str(wav_path),
    ]
    run_cmd(cmd, f"Не удалось конвертировать {media_path.name} в WAV")


def extract_wav_chunk(wav_path: Path, out_chunk: Path, start_sec: float, duration_sec: float) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start_sec),
        "-t",
        str(duration_sec),
        "-i",
        str(wav_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        str(out_chunk),
    ]
    run_cmd(cmd, f"Не удалось выделить кусок аудио ({start_sec}-{start_sec + duration_sec} сек)")


def apply_corrections(text: str, corrections: dict[str, str]) -> str:
    corrected = text or ""
    for wrong, right in corrections.items():
        corrected = re.sub(re.escape(wrong), right, corrected, flags=re.IGNORECASE)
    corrected = re.sub(r"\s+", " ", corrected).strip()
    return corrected


def transcribe_with_giga(
    model,
    wav_path: Path,
    duration: float,
    chunk_seconds: int,
    corrections: dict[str, str],
) -> tuple[List[Segment], str]:
    segments: List[Segment] = []

    # GigaAM short transcribe лимит ~25 сек, поэтому всегда режем на куски
    starts = []
    t = 0.0
    while t < duration:
        starts.append(t)
        t += chunk_seconds

    for idx, start in enumerate(starts, start=1):
        piece = min(chunk_seconds, max(duration - start, 0.1))
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            chunk_path = Path(tmp.name)
        try:
            extract_wav_chunk(wav_path, chunk_path, start, piece)
            try:
                raw = model.transcribe(str(chunk_path))
            except Exception as e:
                print(
                    f"  chunk {idx}/{len(starts)}: ошибка распознавания "
                    f"{round(start,1)}-{round(start + piece,1)} sec -> {e}"
                )
                continue

            text = apply_corrections(raw, corrections)
            if text:
                segments.append(
                    Segment(
                        start_sec=round(start, 2),
                        end_sec=round(start + piece, 2),
                        text=text,
                    )
                )
            print(f"  chunk {idx}/{len(starts)}: {round(start,1)}-{round(start+piece,1)} sec")
        finally:
            try:
                chunk_path.unlink(missing_ok=True)
            except Exception:
                pass

    full_text = " ".join(seg.text for seg in segments).strip()
    return segments, full_text


def do_ocr_from_video(
    video_path: Path,
    out_dir: Path,
    ocr_script: Path,
    interval_sec: int,
    max_frames: int,
) -> tuple[Path, Path]:
    frames_dir = out_dir / "_ocr_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    fps_expr = f"1/{interval_sec}"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vf",
        f"fps={fps_expr}",
        str(frames_dir / "frame_%05d.jpg"),
    ]
    run_cmd(cmd, f"Не удалось извлечь кадры для OCR ({video_path.name})")

    frames = sorted(frames_dir.glob("frame_*.jpg"))
    if max_frames > 0:
        frames = frames[:max_frames]

    ocr_rows = []
    seen = set()
    for i, frame in enumerate(frames, start=1):
        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ocr_script),
            "-ImagePath",
            str(frame),
        ]
        text = run_cmd(cmd, f"Ошибка OCR на кадре {frame.name}")
        text = (text or "").strip()
        if not text or text.upper() == "NO_TEXT":
            continue

        normalized = re.sub(r"\s+", " ", text).strip().lower()
        if normalized in seen:
            continue
        seen.add(normalized)

        ocr_rows.append({
            "frame": frame.name,
            "text": text,
        })
        print(f"  OCR frame {i}/{len(frames)}: {frame.name}")

    ocr_txt = out_dir / f"{safe_stem(video_path.name)}.ocr.txt"
    ocr_json = out_dir / f"{safe_stem(video_path.name)}.ocr.json"

    with open(ocr_txt, "w", encoding="utf-8") as f:
        f.write(f"OCR from video: {video_path.name}\n")
        f.write("=" * 80 + "\n")
        for row in ocr_rows:
            f.write(f"[{row['frame']}]\n{row['text']}\n\n")

    with open(ocr_json, "w", encoding="utf-8") as f:
        json.dump(ocr_rows, f, ensure_ascii=False, indent=2)

    return ocr_txt, ocr_json


def write_vtt(segments: List[Segment], out_path: Path) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for i, seg in enumerate(segments, start=1):
            start = format_vtt_timestamp(seg.start_sec)
            end = format_vtt_timestamp(seg.end_sec)
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{seg.text}\n\n")


def process_file(
    input_item: str,
    model,
    out_root: Path,
    work_dir: Path,
    chunk_seconds: int,
    run_ocr: bool,
    ocr_script: Path,
    ocr_interval: int,
    ocr_max_frames: int,
    corrections: dict[str, str],
) -> FileResult:
    resolved = resolve_input(input_item, work_dir)
    stem = safe_stem(resolved.name)
    out_dir = out_root / stem
    out_dir.mkdir(parents=True, exist_ok=True)

    wav_path = out_dir / f"{stem}.audio16k.wav"
    transcript_txt = out_dir / f"{stem}.transcript.txt"
    transcript_vtt = out_dir / f"{stem}.vtt"
    segments_json = out_dir / f"{stem}.segments.json"

    try:
        duration = media_duration_sec(resolved)
        convert_to_wav16k(resolved, wav_path)
        segments, full_text = transcribe_with_giga(
            model=model,
            wav_path=wav_path,
            duration=duration,
            chunk_seconds=chunk_seconds,
            corrections=corrections,
        )

        with open(transcript_txt, "w", encoding="utf-8") as f:
            f.write(f"Source: {resolved}\n")
            f.write(f"Duration: {round(duration,2)} sec\n")
            f.write("=" * 80 + "\n")
            f.write(full_text + "\n")

        with open(segments_json, "w", encoding="utf-8") as f:
            json.dump([asdict(s) for s in segments], f, ensure_ascii=False, indent=2)

        write_vtt(segments, transcript_vtt)

        ocr_txt_path = None
        ocr_json_path = None
        if run_ocr:
            if resolved.suffix.lower() in {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".webm"}:
                ocr_txt_path, ocr_json_path = do_ocr_from_video(
                    video_path=resolved,
                    out_dir=out_dir,
                    ocr_script=ocr_script,
                    interval_sec=ocr_interval,
                    max_frames=ocr_max_frames,
                )

        return FileResult(
            input=input_item,
            source_file=str(resolved),
            transcript_file=str(transcript_txt),
            transcript_vtt_file=str(transcript_vtt),
            segments_file=str(segments_json),
            ocr_file=str(ocr_txt_path) if ocr_txt_path else None,
            ocr_json_file=str(ocr_json_path) if ocr_json_path else None,
            duration_sec=round(duration, 2),
            segments_count=len(segments),
            language="ru",
            status="ok",
            error=None,
        )

    except Exception as e:
        return FileResult(
            input=input_item,
            source_file=str(resolved) if 'resolved' in locals() else "",
            transcript_file=str(transcript_txt),
            transcript_vtt_file=str(transcript_vtt),
            segments_file=str(segments_json),
            ocr_file=None,
            ocr_json_file=None,
            duration_sec=0.0,
            segments_count=0,
            language="unknown",
            status="error",
            error=str(e),
        )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Giga-first super script: transcription + optional OCR"
    )
    p.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="Список входов: файлы, папки, wildcard-маски или URL",
    )
    p.add_argument(
        "--recursive",
        action="store_true",
        help="Если во входе папка, проходить рекурсивно",
    )
    p.add_argument(
        "--out-dir",
        default=None,
        help="Куда сохранить результаты (по умолчанию: D:/Downloads/_audit/transcribe_<timestamp>)",
    )
    p.add_argument(
        "--model",
        default="v2_rnnt",
        choices=["ctc", "rnnt", "v1_ctc", "v1_rnnt", "v2_ctc", "v2_rnnt"],
        help="Модель GigaAM",
    )
    p.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cuda", "cpu"],
        help="Устройство для модели",
    )
    p.add_argument(
        "--chunk-seconds",
        type=int,
        default=22,
        help="Размер куска аудио в секундах (рекомендуется 20-22)",
    )
    p.add_argument(
        "--ocr",
        action="store_true",
        help="Делать OCR по кадрам видео",
    )
    p.add_argument(
        "--ocr-script",
        default=str(OCR_SCRIPT_DEFAULT),
        help="Путь к готовому OCR PowerShell-скрипту",
    )
    p.add_argument(
        "--ocr-interval",
        type=int,
        default=20,
        help="Интервал между кадрами для OCR (сек)",
    )
    p.add_argument(
        "--ocr-max-frames",
        type=int,
        default=120,
        help="Максимум кадров на файл для OCR",
    )
    p.add_argument(
        "--terms-file",
        default=None,
        help="JSON-файл пользовательских замен терминов",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    ensure_ffmpeg_tools()

    try:
        expanded_inputs = collect_inputs(args.inputs, recursive=args.recursive)
    except Exception as e:
        print(f"Ошибка входных данных: {e}")
        return 2

    try:
        custom_terms = load_custom_terms(Path(args.terms_file)) if args.terms_file else {}
    except Exception as e:
        print(f"Ошибка файла терминов: {e}")
        return 2

    corrections = dict(TOURISM_CORRECTIONS)
    corrections.update(custom_terms)

    try:
        import torch
        from gigaam import load_model
    except Exception as e:
        print("Ошибка: не удалось импортировать gigaam/torch.")
        print("Запускайте этим Python:")
        print(r"D:\Downloads\_SYSTEM\Tools_And_Runtime\_gigaam_venv\Scripts\python.exe")
        print(f"Детали: {e}")
        return 2

    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_root = Path(args.out_dir) if args.out_dir else Path(r"D:\Downloads\_audit") / f"transcribe_{ts}"
    out_root.mkdir(parents=True, exist_ok=True)

    work_dir = out_root / "_downloads"
    work_dir.mkdir(parents=True, exist_ok=True)

    ocr_script = Path(args.ocr_script)
    if args.ocr and not ocr_script.exists():
        print(f"Предупреждение: OCR-скрипт не найден: {ocr_script}. OCR будет пропущен.")
        args.ocr = False

    print(f"Loading GigaAM model: {args.model} on {device}...")
    model = load_model(args.model, device=device)

    summary = {
        "created_at": datetime.now().isoformat(),
        "model": args.model,
        "device": device,
        "chunk_seconds": args.chunk_seconds,
        "ocr_enabled": bool(args.ocr),
        "inputs_count": len(expanded_inputs),
        "terms_count": len(corrections),
        "results": [],
    }

    for idx, item in enumerate(expanded_inputs, start=1):
        print("=" * 80)
        print(f"[{idx}/{len(expanded_inputs)}] Processing: {item}")
        result = process_file(
            input_item=item,
            model=model,
            out_root=out_root,
            work_dir=work_dir,
            chunk_seconds=args.chunk_seconds,
            run_ocr=args.ocr,
            ocr_script=ocr_script,
            ocr_interval=args.ocr_interval,
            ocr_max_frames=args.ocr_max_frames,
            corrections=corrections,
        )
        summary["results"].append(asdict(result))
        print(f"Status: {result.status}")
        if result.error:
            print(f"Error: {result.error}")
        else:
            print(f"Transcript: {result.transcript_file}")
            print(f"Subtitles: {result.transcript_vtt_file}")
            if result.ocr_file:
                print(f"OCR: {result.ocr_file}")

    summary_file = out_root / "summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    summary_csv = out_root / "summary.csv"
    with open(summary_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "input",
                "source_file",
                "status",
                "error",
                "duration_sec",
                "segments_count",
                "transcript_file",
                "transcript_vtt_file",
                "segments_file",
                "ocr_file",
                "ocr_json_file",
            ],
        )
        writer.writeheader()
        for row in summary["results"]:
            writer.writerow({k: row.get(k) for k in writer.fieldnames})

    ok = sum(1 for r in summary["results"] if r["status"] == "ok")
    total = len(summary["results"])
    print("=" * 80)
    print(f"Done: {ok}/{total} successful")
    print(f"Summary: {summary_file}")
    print(f"Summary CSV: {summary_csv}")

    return 0 if ok == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
