#!/usr/bin/env python3
"""
Media validator for Giga transcription pipeline.
Проверяет, что ffprobe видит файл и показывает базовые параметры.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def probe(path: Path) -> dict:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_format",
        "-show_streams",
        "-of", "json",
        str(path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "ffprobe error")
    return json.loads(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate media files for Giga pipeline")
    parser.add_argument("inputs", nargs="+", help="Files to validate")
    args = parser.parse_args()

    ok = 0
    for item in args.inputs:
        p = Path(item)
        print("=" * 70)
        print(f"File: {p}")

        if not p.exists() or not p.is_file():
            print("Status: ERROR (file not found)")
            continue

        try:
            data = probe(p)
            streams = data.get("streams", [])
            fmt = data.get("format", {})
            duration = fmt.get("duration", "?")
            size = fmt.get("size", "?")
            codecs = [s.get("codec_name", "?") for s in streams]

            print("Status: OK")
            print(f"Duration: {duration} sec")
            print(f"Size: {size} bytes")
            print(f"Codecs: {', '.join(codecs) if codecs else 'n/a'}")
            ok += 1
        except Exception as e:
            print(f"Status: ERROR ({e})")

    print("=" * 70)
    print(f"Validated: {ok}/{len(args.inputs)}")
    return 0 if ok == len(args.inputs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
