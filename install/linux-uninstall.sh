#!/usr/bin/env bash
# Remove the Codex Workspace Launcher from this Linux machine.
set -euo pipefail

rm -f "$HOME/.local/bin/codex-workspace"
echo "Removed the codex-workspace command."
echo "The PATH line in ~/.profile / ~/.bashrc is left in place (harmless)."
echo "Your project registry stays in ~/.local/state/codex-workspace-launcher"
echo "(delete that folder to forget all projects)."
