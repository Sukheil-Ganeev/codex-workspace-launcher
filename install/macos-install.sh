#!/usr/bin/env bash
# Codex Workspace Launcher installer (macOS). Run:  bash install/macos-install.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAUNCHER="$REPO/launcher.py"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Run:  brew install python"
  exit 1
fi

# 1) Terminal command:  codex-workspace pick | list | open | add
mkdir -p "$HOME/.local/bin"
WRAPPER="$HOME/.local/bin/codex-workspace"
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
exec python3 "$LAUNCHER" "\$@"
EOF
chmod +x "$WRAPPER"
echo "OK: terminal command installed: $WRAPPER"

# 2) Double-clickable .command on the Desktop (shows the picker)
DESKTOP_CMD="$HOME/Desktop/Codex Workspace.command"
cat > "$DESKTOP_CMD" <<EOF
#!/usr/bin/env bash
cd "\$(dirname "\$0")"
exec python3 "$LAUNCHER" pick
EOF
chmod +x "$DESKTOP_CMD"
echo "OK: Desktop shortcut created: $DESKTOP_CMD"

echo
echo "Done. Use one of:"
echo "  codex-workspace pick      # picker in the terminal"
echo "  double-click 'Codex Workspace.command' on the Desktop"
echo
echo "Add projects:  codex-workspace add /path/to/project --label \"Name\""
echo "Or auto-discover: export CODEX_WORKSPACE_ROOTS=/path/to/parent:/other/parent"
