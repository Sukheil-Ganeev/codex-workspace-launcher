#!/bin/bash
# Установка Yandex Cloud CLI

set -e

echo "=== Yandex Cloud CLI Installer ==="

# Определить OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=linux;;
    Darwin*)    PLATFORM=macos;;
    CYGWIN*|MINGW*|MSYS*)    PLATFORM=windows;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "Detected platform: $PLATFORM"

# Установка
if [ "$PLATFORM" = "linux" ] || [ "$PLATFORM" = "macos" ]; then
    echo "Downloading and installing yc CLI..."
    curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash

    echo ""
    echo "Reloading shell..."
    exec -l $SHELL

elif [ "$PLATFORM" = "windows" ]; then
    echo "For Windows, run in PowerShell (as Administrator):"
    echo "iex (New-Object System.Net.WebClient).DownloadString('https://storage.yandexcloud.net/yandexcloud-yc/install.ps1')"
    exit 0
else
    echo "Unsupported platform: $PLATFORM"
    exit 1
fi

# Проверка установки
echo ""
echo "Checking installation..."
yc version

echo ""
echo "Installation successful!"
echo ""
echo "Next steps:"
echo "1. Run: yc init"
echo "2. Follow the prompts to configure your profile"
echo "3. Start using Yandex Cloud!"
