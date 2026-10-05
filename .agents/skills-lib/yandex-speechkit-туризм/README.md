# Yandex SpeechKit для туризма ОАЭ

Скилл для транскрипции голосовых сообщений через Yandex SpeechKit.

## Структура

```
yandex-speechkit-туризм/
├── SKILL.md                    # Основная документация
├── README.md                   # Это файл
├── assets/
│   ├── templates/             # Шаблоны кода (sync, async, streaming, webhook)
│   └── examples/              # Примеры использования
├── references/
│   ├── faq.md                 # Часто задаваемые вопросы
│   ├── troubleshooting.md     # Решение проблем
│   └── cheatsheet.md          # Шпаргалка
├── scripts/                    # Production automation scripts (NEW!)
│   ├── validate-audio.py      # Validate audio before transcription
│   ├── batch-transcribe.py    # Batch transcription with parallel processing
│   ├── cost-calculator.py     # Cost estimation and comparison
│   ├── benchmark.py           # Performance benchmarking
│   ├── test-all.py            # Test suite
│   ├── deploy-helper.py       # Deployment to Vercel/Netlify/Railway
│   ├── README.md              # Full documentation
│   ├── QUICKSTART.md          # Quick start guide
│   ├── requirements.txt       # Python dependencies
│   ├── setup.sh               # Setup script
│   └── .env.example           # Environment variables template
└── experience/                 # Accumulated experience and lessons
```

## Быстрый старт

### Python API Usage
```python
from speechkit import transcribe_speechkit
text = transcribe_speechkit("voice.ogg")
```

### Automation Scripts
```bash
# Validate audio file
cd scripts/
python validate-audio.py audio.ogg

# Batch transcribe directory
python batch-transcribe.py --input ./audio_files --output results.json

# Calculate costs
python cost-calculator.py --file audio.ogg

# Full documentation
cat scripts/README.md
```

## Связанные скиллы
- ocr-туризм — распознавание текста на изображениях
- whatsapp-парсер — парсинг чатов с транскрипцией
