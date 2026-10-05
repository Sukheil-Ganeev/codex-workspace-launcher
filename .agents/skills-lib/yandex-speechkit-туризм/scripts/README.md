# Yandex SpeechKit Automation Scripts

Production-ready automation scripts for Yandex SpeechKit API integration.

## Prerequisites

```bash
pip install requests rich pydub
```

Optional dependencies:
- `pydub` - Audio file analysis (requires ffmpeg)
- `pytest` - Running tests
- Platform CLIs: `vercel`, `netlify`, `railway` (for deployment)

## Environment Variables

```bash
export YANDEX_API_KEY="your_api_key"
export YANDEX_FOLDER_ID="your_folder_id"
```

---

## Scripts Overview

### 1. validate-audio.py

Validates audio files before transcription.

**Features:**
- Format validation (OGG, MP3, WAV)
- File size checks (max 1 MB for Sync API)
- Duration validation (max 30s for Sync API)
- Sample rate recommendations (48kHz optimal)
- Optimization recommendations with ffmpeg commands

**Usage:**

```bash
# Validate single file
python validate-audio.py audio.ogg

# Validate for specific API type
python validate-audio.py audio.mp3 --api async

# Validate all files in directory
python validate-audio.py --dir ./audio_files

# Export results to JSON
python validate-audio.py --dir ./audio --output validation_results.json

# Verbose mode
python validate-audio.py audio.wav --verbose
```

---

### 2. batch-transcribe.py

Batch transcribe multiple audio files in parallel.

**Features:**
- Parallel processing with configurable workers
- Progress bar with real-time status
- Automatic retry on failures
- Multiple output formats (JSON, CSV, TXT)
- Summary statistics

**Usage:**

```bash
# Basic usage
python batch-transcribe.py \
  --input ./audio_files \
  --output results.json \
  --api-key YOUR_KEY \
  --folder-id YOUR_FOLDER

# Use environment variables
export YANDEX_API_KEY="your_key"
export YANDEX_FOLDER_ID="your_folder"
python batch-transcribe.py --input ./audio --output results.json

# Export to CSV
python batch-transcribe.py \
  --input ./audio \
  --output results.csv \
  --format csv

# Process with 5 parallel workers
python batch-transcribe.py \
  --input ./audio \
  --output results.json \
  --workers 5

# Specify language
python batch-transcribe.py \
  --input ./audio \
  --output results.json \
  --lang en-US
```

**Output Format (JSON):**

```json
[
  {
    "file_name": "audio1.ogg",
    "status": "success",
    "text": "Transcribed text here",
    "duration_sec": 15.5,
    "language": "ru-RU",
    "processing_time_sec": 2.3,
    "timestamp": "2025-02-05 15:30:00"
  }
]
```

---

### 3. cost-calculator.py

Calculate transcription costs and compare with competitors.

**Features:**
- Yandex pricing for all API types (Sync, Async, Streaming)
- Competitor pricing (OpenAI Whisper, Google Speech, AWS Transcribe)
- Audio file duration calculation
- Custom USD/RUB exchange rate
- Cost comparison in RUB and USD

**Usage:**

```bash
# Calculate for 60 seconds
python cost-calculator.py --duration 60

# Calculate from audio file
python cost-calculator.py --file audio.ogg

# Compare only Yandex APIs
python cost-calculator.py --duration 120 --yandex-only

# Custom USD exchange rate
python cost-calculator.py --duration 60 --usd-rate 100
```

**Output:**

```
Cost Comparison
Service              API       Price (RUB)  Price (USD)
Yandex SpeechKit     SYNC            0.48      0.0051
OpenAI Whisper       -               0.57      0.0060
Google Speech        -               0.57      0.0060
AWS Transcribe       -               2.28      0.0240

Best value: Yandex SpeechKit (SYNC)
```

**Pricing (2025):**
- Yandex Sync/Async: 0.12 RUB per 15 seconds
- Yandex Streaming: 0.24 RUB per 15 seconds (2x)
- OpenAI Whisper: $0.006 per minute
- Google Speech: $0.006 per 15 seconds (60 min free/month)
- AWS Transcribe: $0.0004 per second

---

### 4. benchmark.py

Benchmark Yandex SpeechKit performance.

**Features:**
- Test multiple audio files
- Test multiple languages
- Measure processing time and speed ratio
- Calculate costs
- Export results to JSON

**Usage:**

```bash
# Benchmark with default language
python benchmark.py \
  --input ./test_audio \
  --output benchmark_results.json \
  --api-key YOUR_KEY \
  --folder-id YOUR_FOLDER

# Test multiple languages
python benchmark.py \
  --input ./test_audio \
  --languages ru-RU en-US ar-AE \
  --output results.json
```

**Output:**

```
Benchmark Results
File         Language  Duration  Process Time  Speed Ratio  Cost (RUB)  Status
audio1.ogg   ru-RU     15.0s     2.3s          0.15x        0.12        OK
audio1.ogg   en-US     15.0s     2.5s          0.17x        0.12        OK
audio2.mp3   ru-RU     28.5s     3.1s          0.11x        0.24        OK

Average speed ratio: 0.14x (7x faster than real-time)
Average cost per file: 0.16 RUB
Total cost: 0.48 RUB
```

---

### 5. test-all.py

Test suite for Yandex SpeechKit integration.

**Features:**
- Unit tests for API calls
- Mock responses for testing without API
- Cost calculation validation
- Language code format validation

**Usage:**

```bash
# Run all tests
python test-all.py

# Run with pytest
pytest test-all.py -v

# Run specific test
python -m unittest test-all.TestCostCalculation
```

**Output:**

```
Running Yandex SpeechKit Tests...

test_calculate_cost ... ok
test_calculate_units ... ok
test_sync_transcribe_success ... ok

Ran 3 tests in 0.023s
OK

Tests run: 3
Passed: 3
Failed: 0
```

---

### 6. deploy-helper.py

Deploy SpeechKit webhook to serverless platforms.

**Features:**
- Support for Vercel, Netlify, Railway
- CLI availability check
- Health check endpoint

**Usage:**

```bash
# Deploy to Vercel
python deploy-helper.py --platform vercel

# Deploy to Netlify
python deploy-helper.py --platform netlify

# Health check
python deploy-helper.py \
  --platform vercel \
  --health-check \
  --url https://your-app.vercel.app
```

**Prerequisites:**

```bash
npm install -g vercel
npm install -g netlify-cli
npm install -g @railway/cli
```

---

## Common Workflows

### Workflow 1: Validate → Transcribe → Cost

```bash
# 1. Validate audio files
python validate-audio.py --dir ./audio_files

# 2. Transcribe valid files
python batch-transcribe.py \
  --input ./audio_files \
  --output transcriptions.json

# 3. Calculate cost
python cost-calculator.py --file audio1.ogg
```

### Workflow 2: Benchmark Performance

```bash
# Test different languages
python benchmark.py \
  --input ./test_samples \
  --languages ru-RU en-US ar-AE \
  --output benchmark.json

# Analyze results
cat benchmark.json | jq '.[] | {file, language, cost}'
```

### Workflow 3: Production Deployment

```bash
# 1. Run tests
python test-all.py

# 2. Deploy
python deploy-helper.py --platform vercel

# 3. Health check
python deploy-helper.py \
  --platform vercel \
  --health-check \
  --url https://your-app.vercel.app
```

---

## Troubleshooting

### Audio Validation Issues

**Problem:** "Unsupported format"
```bash
# Convert to OGG Opus
ffmpeg -i input.mp3 -c:a libopus -b:a 16k -ar 48000 -ac 1 output.ogg
```

**Problem:** "File too large"
```bash
# Reduce bitrate and convert to mono
ffmpeg -i input.wav -c:a libopus -b:a 16k -ac 1 output.ogg
```

### Batch Transcription Issues

**Problem:** "Rate limit exceeded"
```bash
# Reduce workers
python batch-transcribe.py --input ./audio --workers 1 --output results.json
```

**Problem:** "Authentication failed"
```bash
# Verify credentials
echo $YANDEX_API_KEY
echo $YANDEX_FOLDER_ID
```

---

## Performance Tips

### Optimize Audio Files

```bash
# Best format (smallest size, best quality)
ffmpeg -i input.mp3 -c:a libopus -b:a 16k -ar 48000 -ac 1 output.ogg

# Reduce size for large batches
ffmpeg -i input.wav -c:a libopus -b:a 12k -ar 16000 -ac 1 output.ogg
```

### Batch Processing

- Use 3-5 workers for optimal performance
- Files < 1 MB: Use Sync API
- Files > 1 MB: Use Async API
- Enable retry with `--max-retries 3`

### Cost Optimization

- Use OGG Opus format (smaller files)
- Convert to mono (single channel)
- Lower sample rate for voice: 16kHz
- Avoid Streaming API unless real-time needed

---

## API Rate Limits

- **Sync API:** ~10 requests/second
- **Async API:** ~5 requests/second
- **Streaming API:** ~3 connections/account

---

## Quick Reference

| Script | Purpose | Key Arguments |
|--------|---------|---------------|
| `validate-audio.py` | Validate audio | `--dir`, `--api`, `--output` |
| `batch-transcribe.py` | Batch transcription | `--input`, `--output`, `--workers` |
| `cost-calculator.py` | Cost estimation | `--duration`, `--file` |
| `benchmark.py` | Performance test | `--input`, `--languages` |
| `test-all.py` | Run tests | No arguments |
| `deploy-helper.py` | Deploy webhook | `--platform`, `--url` |

---

**Created:** 2025-02-05
**Python Version:** 3.10+
**Platform:** Cross-platform (Windows, Linux, macOS)
