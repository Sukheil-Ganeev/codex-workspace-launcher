# QUICKSTART — Giga Super Transcribe

## 1) Базовый запуск
```powershell
D:\Downloads\_SYSTEM\Tools_And_Runtime\_gigaam_venv\Scripts\python.exe \
  C:\Users\londo\.codex\skills\giga-transcribe-туризм\scripts\giga_super_transcribe.py \
  --inputs "D:\Downloads\input.mp4"
```

## 2) Два видео + OCR
```powershell
D:\Downloads\_SYSTEM\Tools_And_Runtime\_gigaam_venv\Scripts\python.exe \
  C:\Users\londo\.codex\skills\giga-transcribe-туризм\scripts\giga_super_transcribe.py \
  --inputs "D:\Downloads\video1.mp4" "D:\Downloads\video2.mp4" \
  --ocr
```

## 3) Папка рекурсивно
```powershell
D:\Downloads\_SYSTEM\Tools_And_Runtime\_gigaam_venv\Scripts\python.exe \
  C:\Users\londo\.codex\skills\giga-transcribe-туризм\scripts\giga_super_transcribe.py \
  --inputs "D:\Downloads\incoming" --recursive
```

## 4) Где смотреть результат
- `D:\Downloads\_audit\transcribe_YYYYMMDD_HHMMSS\summary.json`
- `D:\Downloads\_audit\transcribe_YYYYMMDD_HHMMSS\summary.csv`

## 5) Важно
- Яндекс в этом скилле больше не используется.
- Запускать скрипт только через наш Giga venv.
