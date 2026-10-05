---
name: system-maintenance
description: "Windows PC maintenance and disk cleanup orchestrator. Use this skill whenever the user mentions disk space, cleanup, disk analysis, free space, what's taking space, delete junk, find duplicates, clear cache, system optimization, PC maintenance, slow computer, or wants to organize files. Also triggers for mentions of specific tools: dust, WizTree, Czkawka, BleachBit, cc-cleaner, WinUtil, Win11Debloat. Even if the user just says 'clean up' or 'my disk is full' — use this skill."
---

# System Maintenance — Windows PC Toolkit

You have a full set of installed tools for disk analysis, cleanup, duplicate detection, and system optimization. This skill tells you which tool to use, when, and how.

## Quick Decision Tree

```
User wants to know what's taking space?
  → dust (fast CLI overview)
  → WizTree (detailed CSV, MFT-based, 5 sec for 1TB)

User wants to find duplicates?
  → Czkawka CLI (hash-based duplicate search)

User wants to clean caches?
  → cc-cleaner (dev/AI caches: Claude, Whisper, Huggingface, npm, pip)
  → BleachBit (system caches: browsers, temp, logs)

User wants to organize files?
  → file-organizer skill

User wants to optimize Windows?
  → WinUtil (tweaks, debloat, telemetry)
  → Win11Debloat (remove pre-installed apps)
```

## Tools Registry

### 1. dust — Fast Disk Usage (USE FIRST for any disk question)

The go-to tool for "what's eating my disk?" questions. 10x faster than `du`.

```bash
# Path (use full path in current session, after terminal restart just `dust`):
DUST="/c/Users/londo/AppData/Local/Microsoft/WinGet/Packages/bootandy.dust_Microsoft.Winget.Source_8wekyb3d8bbwe/dust-v1.2.4-x86_64-pc-windows-gnu/dust.exe"

# Quick overview — top 25 folders, depth 1:
$DUST -d 1 -n 25 /d/

# Deeper scan — depth 2:
$DUST -d 2 -n 30 /c/Users/londo/

# Specific folder:
$DUST -d 2 -n 20 /d/Downloads/
```

**When to use:** Always first. Before anything else — understand what's big.
**Output:** Visual tree with sizes and bars. Perfect for quick decisions.

### 2. WizTree — MFT-Based Full Disk Scan

Reads the NTFS Master File Table directly — scans 1TB in 5 seconds. Nothing is faster.

```bash
# CLI CSV export (works reliably for C: drive):
"D:/Programs/WizTree/WizTree64.exe" "C:" /export="D:/Downloads/wiztree_C.csv" /admin=0 /sort=2

# For D: drive — CLI export may open GUI instead. Use dust for D: or ask user to export manually.
```

**When to use:** When you need a complete file-level inventory of a drive. Especially useful for C: drive analysis.
**Limitation:** CLI export only reliably works for C: drive. For D: drive, use dust or ask the user to export via GUI.
**GUI location:** `D:/Programs/WizTree/WizTree64.exe`

### 3. Czkawka — Duplicate & Junk Finder

Finds duplicates by hash, similar images, empty folders, temp files. CLI and GUI available.

```bash
CLI="D:/Programs/Czkawka/czkawka_cli.exe"

# Find duplicate files (50MB+, hash-based):
$CLI dup -d /d/Downloads -m 52428800 -s HASH -f /d/Downloads/results_duplicates.txt

# Find empty folders:
$CLI empty-folders -d /d/ -f /d/Downloads/results_empty.txt

# Find temp files:
$CLI temp -d /c/Users/londo -d /d/ -f /d/Downloads/results_temp.txt

# Find biggest files (top 50):
$CLI big -d /d/Downloads -n 50 -f /d/Downloads/results_big.txt

# Auto-delete duplicates (keep oldest):
$CLI dup -d /d/Downloads -m 52428800 -s HASH -D aeo
```

**Syntax notes:**
- Directories: separate `-d` flags for each path (NOT comma-separated)
- Exclusions: separate `-e` flags
- Minimum size: `-m` in bytes (52428800 = 50MB, 10485760 = 10MB)
- Search method: `-s HASH` (accurate) or `-s SIZE` (fast but less precise)

**When to use:** After dust shows the big folders — dive into those folders with Czkawka to find duplicates.
**GUI:** `D:/Programs/Czkawka/krokiet.exe` — for visual duplicate review

### 4. cc-cleaner — Developer Cache Cleaner

Cleans AI model caches, Claude logs, npm/pip/cargo caches.

```bash
# Show what can be cleaned:
cc-cleaner status

# Clean everything:
cc-cleaner clean --all

# Clean specific:
cc-cleaner clean claude
cc-cleaner clean whisper
cc-cleaner clean huggingface
```

**Typical savings:** 5-20 GB depending on AI model usage.
**When to use:** After disk analysis if dev/AI caches show up as space hogs.

### 5. BleachBit — System Cache Cleaner

Cleans browser caches, system temp files, application logs. Like CCleaner but open-source.

```bash
BLEACH="C:/Users/londo/AppData/Local/BleachBit/bleachbit.exe"

# Preview what would be cleaned:
$BLEACH --preview

# Clean system temp:
$BLEACH --clean system.tmp

# Clean specific:
$BLEACH --clean firefox.cache
$BLEACH --clean google_chrome.cache
```

**When to use:** For system-level cleanup (temp files, browser caches, logs).
**Note:** Some operations need Admin rights.

### 6. file-organizer (Claude Code Skill)

Smart file sorting — categorizes files by type, finds duplicates, suggests folder structure.

**When to use:** After cleanup, to organize what remains. Great for messy Downloads folders.
**Invoke:** This is a Claude Code skill — it activates automatically when organizing files.

### 7. WinUtil — Windows Optimization

Chris Titus Tech's all-in-one Windows utility. GUI tool with tweaks, debloat, app installation.

```bash
# Launch (needs Admin PowerShell):
powershell -ExecutionPolicy Bypass -File D:\Downloads\winutil.ps1
```

**When to use:** One-time system optimization. Tabs: Install (bulk app install), Tweaks (disable telemetry, optimize services), Updates (configure Windows Update), Config (system features).
**Best preset:** Tweaks → Standard → Run Tweaks

### 8. Win11Debloat — Remove Bloatware

Simple PowerShell script to remove pre-installed Windows apps and disable telemetry.

```bash
# Launch (double-click, needs Admin):
# D:\Programs\Win11Debloat\Win11Debloat-master\Run.bat
```

**When to use:** First-time setup or after major Windows update added back bloatware.

## Standard Cleanup Workflow

When the user wants a general cleanup, follow this order:

### Phase 1: Analyze (understand before deleting)
1. Run `dust -d 1 -n 25` on the target drive
2. Identify the biggest folders
3. Present findings to user

### Phase 2: Quick Wins (safe, automatic)
1. `cc-cleaner clean --all` — dev/AI caches
2. Clean browser caches (rm Cache/Code Cache folders, skip Yandex Browser)
3. Clean Windows temp: `rm -rf /c/Users/londo/AppData/Local/Temp/*`
4. Empty recycle bins

### Phase 3: Find Waste (needs user approval)
1. Run Czkawka duplicate scan on large folders
2. Present duplicate groups with sizes
3. Ask user which to delete

### Phase 4: Organize (optional)
1. Use file-organizer skill on Downloads
2. Archive old files

### Phase 5: System Optimization (one-time)
1. WinUtil tweaks (Standard preset)
2. Win11Debloat if needed
3. chkdsk if NTFS issues detected

## Drive Layout

| Drive | Size | Purpose | Key folders |
|-------|------|---------|-------------|
| C: | 931 GB | System, games, Adobe | Windows, Games, Program Files |
| D: | 1.9 TB | Downloads, projects, data | Downloads (largest!), Projects, Programs |

## Key Paths

- User home: `C:/Users/londo/`
- Downloads: `D:/Downloads/`
- Installed programs: `D:/Programs/`
- Skills: `C:/Users/londo/.claude/skills/`
- AppData Local: `C:/Users/londo/AppData/Local/`
- Browser caches: `AppData/Local/Google/Chrome/`, `AppData/Local/BraveSoftware/`, `AppData/Local/Microsoft/Edge/`

## Common Patterns

**"My disk is full"** → dust overview → identify biggest consumers → present options

**"Find duplicates"** → Czkawka dup with HASH method → present groups → delete with user approval

**"Clean everything"** → Phase 1-3 workflow above

**"What's taking space in Downloads?"** → `dust -d 2 -n 30 /d/Downloads/`

**"Clear caches"** → cc-cleaner status → cc-cleaner clean → BleachBit if more needed

**"Optimize Windows"** → WinUtil → Tweaks → Standard

---

## Lessons Learned (Session 2026-03-30)

Real experience from cleaning C: (0 → 174 ГБ) and D: (30 → 457 ГБ). Apply these lessons.

### Tool Selection Order Matters

1. **NEVER start with `du`** for full disk analysis. It's 10-100x slower than dust/WizTree on large drives. A 1.9 TB drive took 40+ minutes with `du` vs seconds with dust.
2. **dust first, always.** `dust -d 1 -n 25 /drive/` gives instant overview.
3. **WizTree for C: drive CSV** — CLI export works. For D: — use dust or ask user to do WizTree GUI export.
4. **Czkawka AFTER dust** — only scan folders that dust showed are big. Don't scan entire drives blindly.

### Biggest Space Hogs Found (typical Windows PC)

| Category | Typical Size | Where | Action |
|----------|-------------|-------|--------|
| iTunes/iPhone backups | 100-700 ГБ | D:\iTunesBackup | Ask if iCloud backup exists, then delete |
| Docker docker_data.vhdx | 20-100 ГБ | AppData\Local\Docker | `docker system prune -a` or delete vhdx |
| Games | 50-200 ГБ per game | C:\Games, Program Files | Move to D: or uninstall |
| $Extend\$Deleted (NTFS) | 10-70 ГБ | C:\ (hidden) | `chkdsk C: /F` at reboot |
| WhatsApp PDF duplicates | 10-40 ГБ | iPhone backup folders | Same PDF sent to N contacts = N copies. Czkawka dedup. |
| node_modules | 1-10 ГБ | scattered | Safe to delete, rebuild with `npm install` |
| AI model caches | 5-20 ГБ | AppData | `cc-cleaner clean --all` |
| Browser caches | 3-10 ГБ | AppData\Local\{Chrome,Brave,Edge} | rm Cache/Code Cache folders. Skip Yandex Browser! |
| .rar installer archives | 5-30 ГБ | D:\ root, Downloads | Delete after software installed |
| DJI drone footage | 10-100 ГБ | Downloads | Archive to external drive |
| Old installers (.exe, .iso) | 5-20 ГБ | Downloads | Delete after use |

### Deletion Speed Warning

**iTunes backups are SLOW to delete** (~2 million tiny files). `rm -rf` on 679 ГБ iTunes backup took ~45 minutes. This is normal — NTFS is slow with millions of small files. No tool makes this faster. Warn the user and run in background.

### Browser Cache Cleanup

**Always skip Yandex Browser** — user explicitly requested this. Clean Chrome, Brave, Edge only:
```bash
# Safe to delete (passwords, bookmarks, extensions are NOT affected):
rm -rf "AppData/Local/Google/Chrome/User Data/Default/Cache/"*
rm -rf "AppData/Local/Google/Chrome/User Data/Default/Code Cache/"*
rm -rf "AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/Cache/"*
rm -rf "AppData/Local/Microsoft/Edge/User Data/Default/Cache/"*
```

### Czkawka Auto-Delete

The `-D aeo` flag (Delete All Except Oldest) works well for mass deduplication:
```bash
# Safe auto-delete: keeps oldest copy in each duplicate group
czkawka_cli.exe dup -d /path -m 52428800 -s HASH -D aeo
```
This cleaned 74.5 ГБ of duplicates (872 files in 162 groups) in one command.

### WhatsApp Business Backup Pattern

iPhone WhatsApp Business backups store **one copy of each sent file per contact**. A 116 MB PDF sent to 77 contacts = 77 × 116 MB = 8.7 ГБ of identical files. Czkawka hash dedup catches all of these.

### Docker: Check Before Cleaning

Docker Desktop creates a growing `docker_data.vhdx` virtual disk that never shrinks. If Docker is not actively used:
1. Check if Docker daemon is running
2. If not running and not needed — delete the vhdx directly
3. If running — `docker system prune -a --volumes -f`
In our case: Docker was installed but stopped. The vhdx was 60 ГБ of wasted space.

### NTFS $Extend\$Deleted

WizTree may show `C:\$Extend\$Deleted` taking 10-70 ГБ. This is orphaned NTFS metadata from deleted files. Fix: `chkdsk C: /F` (requires reboot for system drive). Schedule before a planned reboot.

### MCP Servers Installed

Two MCP servers are configured in settings.json (activate after restart):
- **powershell-mcp**: `node D:/Programs/mcp-servers/powershell-mcp/src/server.js`
- **desktop-commander**: `node D:/Programs/mcp-servers/desktop-commander-mcp/dist/index.js`

### cc-cleaner DELETES Claude Code session history!

**CRITICAL:** `cc-cleaner clean` удаляет Claude transcripts (`.jsonl` файлы сессий). После очистки — `/resume` не находит старые сессии, они потеряны навсегда.

**Перед запуском cc-cleaner:**
1. Спросить пользователя: "cc-cleaner удалит историю сессий Claude Code. Продолжить?"
2. Или использовать `cc-cleaner clean` с конкретными целями (whisper, huggingface) вместо `--all`
3. Не чистить `claude` категорию если пользователь хочет сохранить историю сессий

### Hyper-V on Windows 11 Home

Cowork requires full Hyper-V (not available on Home). Hack exists:
- Batch file at `D:\Downloads\enable-hyperv.bat` installs Hyper-V packages via DISM
- Run as Admin → restart. Some 0x80070002 errors on language packs are non-critical.
- May break after major Windows updates. Upgrade to Pro ($12-20 from key resellers) for permanent fix.
