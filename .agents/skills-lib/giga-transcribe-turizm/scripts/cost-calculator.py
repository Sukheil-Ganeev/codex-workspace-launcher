#!/usr/bin/env python3
"""
Cost estimator for local Giga transcription.
Прямых API-расходов нет (локальный запуск), только оценка времени.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def duration_sec(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    return float(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate local transcription runtime")
    parser.add_argument("files", nargs="+", help="Audio/video files")
    parser.add_argument("--rtf", type=float, default=0.40, help="Expected realtime factor (wall/audio)")
    args = parser.parse_args()

    total = 0.0
    for item in args.files:
        p = Path(item)
        if not p.exists():
            print(f"Skip missing: {p}")
            continue
        d = duration_sec(p)
        total += d
        print(f"{p.name}: {d/60:.2f} min")

    wall = total * args.rtf
    print("-" * 60)
    print(f"Total audio: {total/60:.2f} min")
    print(f"Expected wall time (~rtf={args.rtf}): {wall/60:.2f} min")
    print("Direct API cost: 0 (local GigaAM)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
