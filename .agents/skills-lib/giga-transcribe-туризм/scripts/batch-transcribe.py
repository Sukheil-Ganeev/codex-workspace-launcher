#!/usr/bin/env python3
"""
Legacy wrapper.
Этот файл сохранен для обратной совместимости и перенаправляет на giga_super_transcribe.py.
"""

from pathlib import Path
import subprocess
import sys


def main() -> int:
    target = Path(__file__).with_name("giga_super_transcribe.py")
    print("[INFO] batch-transcribe.py переведен в legacy-режим.")
    print("[INFO] Используем единый скрипт: giga_super_transcribe.py")

    if not target.exists():
        print(f"[ERROR] Не найден {target}")
        return 2

    args = sys.argv[1:]
    if not args:
        cmd = [sys.executable, str(target), "--help"]
    elif "--inputs" in args:
        cmd = [sys.executable, str(target), *args]
    else:
        cmd = [sys.executable, str(target), "--inputs", *args]

    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
