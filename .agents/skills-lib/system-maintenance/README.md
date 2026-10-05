# system-maintenance

Windows PC maintenance and disk cleanup orchestrator for Claude Code.

## What it does

Orchestrates 9 installed tools for disk analysis, cleanup, duplicate detection, and Windows optimization. Knows which tool to use for each situation and the correct command syntax.

## Installed Tools

| Tool | Type | Purpose |
|------|------|---------|
| dust | Rust CLI | Fast disk usage analysis |
| WizTree | Windows app | MFT-based full disk scan (5 sec/TB) |
| Czkawka | Rust CLI+GUI | Duplicate/temp/empty folder finder |
| cc-cleaner | Python CLI | Developer cache cleaner |
| BleachBit | App + CLI | System cache cleaner |
| disk-cleaner | Claude skill | AI-powered disk analysis |
| file-organizer | Claude skill | Smart file sorting |
| WinUtil | PowerShell | Windows optimization GUI |
| Win11Debloat | PowerShell | Remove Windows bloatware |

## Usage

The skill triggers automatically when you mention disk space, cleanup, duplicates, caches, or system optimization.

## Trigger phrases

- "what's taking space"
- "disk is full"
- "clean up"
- "find duplicates"
- "clear cache"
- "optimize Windows"
- "my computer is slow"
- "free up space"
