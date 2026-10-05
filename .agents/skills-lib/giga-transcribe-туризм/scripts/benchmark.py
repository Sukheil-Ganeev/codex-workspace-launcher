#!/usr/bin/env python3
"""
Light benchmark for local Giga pipeline.
Оценивает время обработки и соотношение realtime factor.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
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
    parser = argparse.ArgumentParser(description="Benchmark giga_super_transcribe.py")
    parser.add_argument("--files", nargs="+", required=True)
    parser.add_argument("--chunk-seconds", type=int, default=22)
    args = parser.parse_args()

    script = Path(__file__).with_name("giga_super_transcribe.py")
    if not script.exists():
        print(f"Script not found: {script}")
        return 2

    total_audio = 0.0
    total_wall = 0.0

    for item in args.files:
        p = Path(item)
        if not p.exists():
            print(f"Skip missing: {p}")
            continue

        aud = duration_sec(p)
        total_audio += aud

        t0 = time.time()
        cmd = [
            sys.executable,
            str(script),
            "--inputs",
            str(p),
            "--chunk-seconds",
            str(args.chunk_seconds),
        ]
        code = subprocess.call(cmd)
        elapsed = time.time() - t0
        total_wall += elapsed

        rtf = elapsed / aud if aud > 0 else 0
        print(f"{p.name}: audio={aud:.1f}s wall={elapsed:.1f}s rtf={rtf:.2f} status={code}")

    print("-" * 70)
    total_rtf = total_wall / total_audio if total_audio > 0 else 0
    print(f"TOTAL: audio={total_audio:.1f}s wall={total_wall:.1f}s rtf={total_rtf:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
