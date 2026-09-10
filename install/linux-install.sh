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

# Make sure ~/.local/bin is on PATH (most distros have it; older ones may not)
if ! command -v codex-workspace >/dev/null 2>&1; then
  for rc in "$HOME/.profile" "$HOME/.bashrc"; do
    [ -f "$rc" ] || touch "$rc"
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$rc"; then
      printf '\n# codex-workspace launcher\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$rc"
      echo "OK: PATH updated in $rc"
    fi
  done
fi

echo "OK: terminal command installed: $WRAPPER"
echo
echo "Use:"
echo "  codex-workspace pick               # picker (project + tool + mode)"
echo "  codex-workspace list               # projects with status"
echo "  codex-workspace add /path --label \"Name\""
echo "  codex-workspace tools              # all AI tools with versions"
echo "To remove: bash install/linux-uninstall.sh"
