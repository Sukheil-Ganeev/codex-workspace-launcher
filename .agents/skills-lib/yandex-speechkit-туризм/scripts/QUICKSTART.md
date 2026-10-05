# Quick Start Guide

## Installation (1 minute)

```bash
cd scripts/

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
nano .env  # Add your YANDEX_API_KEY and YANDEX_FOLDER_ID

# Set environment variables
export YANDEX_API_KEY="your_api_key"
export YANDEX_FOLDER_ID="your_folder_id"
```

## Common Use Cases

### 1. Validate Audio File (before transcription)

```bash
python validate-audio.py audio.ogg
```

Output: VALID/INVALID + recommendations

### 2. Transcribe Single File (manual)

See templates in `../assets/templates/` for API examples.

### 3. Batch Transcribe Directory

```bash
python batch-transcribe.py \
  --input ./audio_files \
  --output transcriptions.json
```

Output: JSON with all transcriptions

### 4. Calculate Cost

```bash
# From file
python cost-calculator.py --file audio.ogg

# From duration
python cost-calculator.py --duration 60
```

Output: Cost in RUB and USD with comparison

### 5. Benchmark Performance

```bash
python benchmark.py \
  --input ./test_audio \
  --output benchmark.json
```

Output: Performance metrics and costs

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "API authentication failed"
```bash
# Check credentials
echo $YANDEX_API_KEY
echo $YANDEX_FOLDER_ID
```

### "Unsupported audio format"
```bash
# Convert to OGG Opus
ffmpeg -i input.mp3 -c:a libopus -b:a 16k -ar 48000 -ac 1 output.ogg
```

## Need Help?

- Full documentation: `README.md`
- Script help: `python script.py --help`
- Skill reference: `../SKILL.md`
