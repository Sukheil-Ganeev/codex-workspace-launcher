#!/usr/bin/env bash
# Codex Workspace Launcher installer (Linux). Run:  bash install/linux-install.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAUNCHER="$REPO/launcher.py"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Install it first (apt install python3)."
  exit 1
fi

mkdir -p "$HOME/.local/bin"
WRAPPER="$HOME/.local/bin/codex-workspace"
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
exec python3 "$LAUNCHER" "\$@"
EOF
chmod +x "$WRAPPER"

echo "OK: terminal command installed: $WRAPPER"
echo
echo "Use:  codex-workspace pick"
echo "Add projects:  codex-workspace add /path/to/project --label \"Name\""
echo "Auto-discover: export CODEX_WORKSPACE_ROOTS=/path/to/parent:/other/parent"
