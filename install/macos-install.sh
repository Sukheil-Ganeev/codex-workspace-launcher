#!/usr/bin/env bash
# Codex Workspace Launcher installer (macOS). Run:  bash install/macos-install.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAUNCHER="$REPO/launcher.py"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Run:  brew install python"
  exit 1
fi

# 1) Terminal command:  codex-workspace pick | list | add | open | tools
mkdir -p "$HOME/.local/bin"
WRAPPER="$HOME/.local/bin/codex-workspace"
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
exec python3 "$LAUNCHER" "\$@"
EOF
chmod +x "$WRAPPER"
echo "OK: terminal command installed: $WRAPPER"

# 2) Double-clickable .command on the Desktop (shows the picker window)
DESKTOP_CMD="$HOME/Desktop/Codex Workspace.command"
cat > "$DESKTOP_CMD" <<EOF
#!/usr/bin/env bash
exec python3 "$LAUNCHER" pick
EOF
chmod +x "$DESKTOP_CMD"
echo "OK: Desktop shortcut created: $DESKTOP_CMD"

echo
echo "Done. Use:"
echo "  codex-workspace pick               # picker (project + tool + mode)"
echo "  codex-workspace list               # projects with status"
echo "  codex-workspace add /path --label \"Name\""
echo "  codex-workspace open <id> --tool claude --mode safe"
echo "  codex-workspace tools              # all AI tools with versions"
echo "  codex-workspace doctor             # health checks"
