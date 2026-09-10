#!/usr/bin/env bash
# Remove the Codex Workspace Launcher from this Mac.
set -euo pipefail

rm -f "$HOME/.local/bin/codex-workspace"
rm -f "$HOME/Desktop/Codex Workspace.command"
echo "Removed command and Desktop shortcut."
echo "The PATH line in ~/.zprofile or ~/.zshrc is left in place (harmless);"
echo "remove the two '# codex-workspace launcher' lines manually if you want."
echo "Your project registry stays in ~/.local/state/codex-workspace-launcher"
echo "(delete that folder to forget all projects)."
