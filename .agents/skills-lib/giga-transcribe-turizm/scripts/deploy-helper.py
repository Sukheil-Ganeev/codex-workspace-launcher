#!/usr/bin/env python3
"""
Legacy helper kept for compatibility.
Деплой не требуется: transcription pipeline запускается локально.
"""


def main() -> int:
    print("Этот pipeline рассчитан на локальный запуск через giga venv.")
    print("Используйте giga_super_transcribe.py напрямую.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
