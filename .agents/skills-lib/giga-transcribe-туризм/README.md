# Giga Super Transcribe Skill (legacy folder name)

Папка исторически называется `giga-transcribe-туризм`, но скилл переведен в **GigaAM-only** режим.

## Что внутри важно сейчас
- `SKILL.md` — актуальные инструкции для агента.
- `scripts/giga_super_transcribe.py` — единый рабочий скрипт транскрибации + OCR.
- `scripts/README.md` — примеры запуска.
- `scripts/QUICKSTART.md` — быстрый старт.

## Что больше не используем
- Yandex SpeechKit и любые `YANDEX_*` ключи.

## Рекомендуемый запуск
```powershell
D:\Downloads\_SYSTEM\Tools_And_Runtime\_gigaam_venv\Scripts\python.exe \
  C:\Users\londo\.codex\skills\giga-transcribe-туризм\scripts\giga_super_transcribe.py \
  --inputs "D:\Downloads\video1.mp4" "D:\Downloads\video2.mp4" --ocr
```
