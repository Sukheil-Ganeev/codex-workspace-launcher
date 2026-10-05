# Giga Super Transcribe Scripts

Этот каталог переведен в режим **Giga-only**.

Важно:
- Yandex SpeechKit больше не используется.
- Основной и рекомендованный скрипт: `giga_super_transcribe.py`.

## Главный скрипт
`giga_super_transcribe.py` объединяет в одном месте:
- транскрибацию аудио/видео через GigaAM;
- нарезку длинных файлов на чанки;
- генерацию `.transcript.txt`, `.segments.json`, `.vtt`;
- OCR по кадрам видео (опционально);
- сводные отчеты `summary.json` и `summary.csv`.

## Рекомендуемый запуск (Windows)
```powershell
D:\Downloads\_SYSTEM\Tools_And_Runtime\_gigaam_venv\Scripts\python.exe \
  C:\Users\londo\.codex\skills\giga-transcribe-туризм\scripts\giga_super_transcribe.py \
  --inputs "D:\Downloads\video1.mp4" "D:\Downloads\video2.mp4" \
  --ocr
```

## Частые сценарии
### 1) Пакетно из папки
```powershell
D:\Downloads\_SYSTEM\Tools_And_Runtime\_gigaam_venv\Scripts\python.exe \
  C:\Users\londo\.codex\skills\giga-transcribe-туризм\scripts\giga_super_transcribe.py \
  --inputs "D:\Downloads\incoming" --recursive
```

### 2) С OCR + больше редких кадров
```powershell
D:\Downloads\_SYSTEM\Tools_And_Runtime\_gigaam_venv\Scripts\python.exe \
  C:\Users\londo\.codex\skills\giga-transcribe-туризм\scripts\giga_super_transcribe.py \
  --inputs "D:\Downloads\car.mp4" --ocr --ocr-interval 15 --ocr-max-frames 180
```

### 3) Свой словарь терминов
```powershell
D:\Downloads\_SYSTEM\Tools_And_Runtime\_gigaam_venv\Scripts\python.exe \
  C:\Users\londo\.codex\skills\giga-transcribe-туризм\scripts\giga_super_transcribe.py \
  --inputs "D:\Downloads\audio.wav" --terms-file "D:\Downloads\custom_terms.json"
```

Пример `custom_terms.json`:
```json
{
  "ибан": "IBAN",
  "эмирейтс нбд": "Emirates NBD"
}
```

## Что сохраняется
По умолчанию:
- `D:\Downloads\_audit\transcribe_YYYYMMDD_HHMMSS\...`

На каждый входной файл:
- `<name>.transcript.txt`
- `<name>.segments.json`
- `<name>.vtt`
- `<name>.ocr.txt` (если `--ocr`)
- `<name>.ocr.json` (если `--ocr`)

Сводно:
- `summary.json`
- `summary.csv`

## Примечание по старым скриптам
Старые скрипты оставлены только для справки. Рабочий стандарт — `giga_super_transcribe.py`.
