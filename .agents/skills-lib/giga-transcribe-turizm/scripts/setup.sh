#!/bin/bash
# Setup helper for Giga transcription scripts

set -e

echo "Setting up Giga transcription scripts..."

python3 --version || true

if command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg: $(ffmpeg -version | head -n 1)"
else
  echo "WARNING: ffmpeg not found"
fi

if command -v ffprobe >/dev/null 2>&1; then
  echo "ffprobe: OK"
else
  echo "WARNING: ffprobe not found"
fi

pip install -r requirements.txt || true

echo "Run smoke tests:"
echo "  python3 test-all.py"

echo "Main command:"
echo "  python3 giga_super_transcribe.py --help"
