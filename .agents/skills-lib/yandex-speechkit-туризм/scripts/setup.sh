#!/bin/bash
# Setup script for Yandex SpeechKit automation scripts

echo "Setting up Yandex SpeechKit automation scripts..."

# Check Python version
echo "Checking Python version..."
python3 --version

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check ffmpeg
echo "Checking ffmpeg installation..."
if command -v ffmpeg &> /dev/null; then
    echo "ffmpeg is installed: $(ffmpeg -version | head -n 1)"
else
    echo "WARNING: ffmpeg is not installed"
    echo "Audio validation will not work without ffmpeg"
    echo "Install ffmpeg:"
    echo "  - Windows: choco install ffmpeg"
    echo "  - macOS: brew install ffmpeg"
    echo "  - Linux: apt-get install ffmpeg"
fi

# Check environment variables
echo ""
echo "Checking environment variables..."
if [ -z "$YANDEX_API_KEY" ]; then
    echo "WARNING: YANDEX_API_KEY not set"
else
    echo "YANDEX_API_KEY is set"
fi

if [ -z "$YANDEX_FOLDER_ID" ]; then
    echo "WARNING: YANDEX_FOLDER_ID not set"
else
    echo "YANDEX_FOLDER_ID is set"
fi

# Copy .env.example if .env doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your credentials"
fi

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x *.py

# Run tests
echo ""
echo "Running tests..."
python3 test-all.py

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Yandex Cloud credentials"
echo "2. Source the environment: source .env"
echo "3. Run a script: python3 validate-audio.py --help"
