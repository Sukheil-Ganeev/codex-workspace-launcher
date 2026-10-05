#!/usr/bin/env python3
"""
Smoke tests for Giga transcription toolchain.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], title: str) -> bool:
    print(f"[TEST] {title}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0:
        print("  OK")
        return True
    print("  FAIL")
    if proc.stderr:
        print("  STDERR:", proc.stderr.strip())
    return False


def main() -> int:
    script = Path(__file__).with_name("giga_super_transcribe.py")

    checks = [
        run(["ffmpeg", "-version"], "ffmpeg available"),
        run(["ffprobe", "-version"], "ffprobe available"),
        run([sys.executable, "-c", "import gigaam, torch; print('ok')"], "gigaam+torch import"),
        run([sys.executable, str(script), "--help"], "super script --help"),
    ]

    passed = sum(1 for x in checks if x)
    total = len(checks)
    print(f"Result: {passed}/{total} tests passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
