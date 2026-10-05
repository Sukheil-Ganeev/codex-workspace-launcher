param(
    [string]$SkillPath = (Join-Path $PSScriptRoot '..')
)

$ErrorActionPreference = 'Stop'

function Add-ErrorLine {
    param([System.Collections.Generic.List[string]]$List, [string]$Message)
    $List.Add($Message) | Out-Null
}

function Add-WarningLine {
    param([System.Collections.Generic.List[string]]$List, [string]$Message)
    $List.Add($Message) | Out-Null
}

$errors = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

try {
    $resolvedSkillPath = (Resolve-Path -LiteralPath $SkillPath).Path
} catch {
    Write-Error "Skill path not found: $SkillPath"
    exit 1
}

$skillDir = Get-Item -LiteralPath $resolvedSkillPath
$skillName = $skillDir.Name
$skillFile = Join-Path $resolvedSkillPath 'SKILL.md'

if (-not (Test-Path -LiteralPath $skillFile)) {
    Add-ErrorLine $errors "Missing required file: SKILL.md"
}

$reparsePoints = Get-ChildItem -LiteralPath $resolvedSkillPath -Recurse -Force | Where-Object {
    $_.Attributes -band [IO.FileAttributes]::ReparsePoint
}

if ($reparsePoints) {
    foreach ($item in $reparsePoints) {
        Add-ErrorLine $errors "Symlink or reparse point is not allowed: $($item.FullName)"
    }
}

if (Test-Path -LiteralPath $skillFile) {
    $skillContent = Get-Content -LiteralPath $skillFile -Raw
    $frontmatterMatch = [regex]::Match($skillContent, "(?s)^---\r?\n(.*?)\r?\n---\r?\n")

    if (-not $frontmatterMatch.Success) {
        Add-ErrorLine $errors "SKILL.md is missing valid YAML frontmatter."
    } else {
        $frontmatter = $frontmatterMatch.Groups[1].Value
        $frontmatterKeys = [regex]::Matches($frontmatter, "(?m)^([A-Za-z0-9_-]+):") | ForEach-Object {
            $_.Groups[1].Value
        }

        $nameMatch = [regex]::Match($frontmatter, "(?m)^name:\s*(.+?)\s*$")
        $descriptionMatch = [regex]::Match($frontmatter, "(?m)^description:\s*(.+?)\s*$")

        if (-not $nameMatch.Success) {
            Add-ErrorLine $errors "Frontmatter is missing 'name'."
        }

        if (-not $descriptionMatch.Success) {
            Add-ErrorLine $errors "Frontmatter is missing 'description'."
        }

        if ($frontmatterKeys.Count -gt 2) {
            $extra = $frontmatterKeys | Where-Object { $_ -notin @('name', 'description') }
            foreach ($item in $extra) {
                Add-WarningLine $warnings "Extra frontmatter field found: $item"
            }
        }

        if ($nameMatch.Success) {
            $frontmatterName = $nameMatch.Groups[1].Value.Trim()

            if ($frontmatterName -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') {
                Add-ErrorLine $errors "Frontmatter name must be kebab-case: $frontmatterName"
            }

            if ($frontmatterName.Length -gt 64) {
                Add-ErrorLine $errors "Frontmatter name is longer than 64 characters."
            }

            if ($frontmatterName -ne $skillName) {
                Add-ErrorLine $errors "Folder name '$skillName' does not match frontmatter name '$frontmatterName'."
            }
        }

        if ($descriptionMatch.Success) {
            $description = $descriptionMatch.Groups[1].Value.Trim()

            if ([string]::IsNullOrWhiteSpace($description)) {
                Add-ErrorLine $errors "Frontmatter description must not be empty."
            }

            if ($description.Length -gt 1024) {
                Add-ErrorLine $errors "Frontmatter description is longer than 1024 characters."
            }
        }
    }
}

$textFiles = Get-ChildItem -LiteralPath $resolvedSkillPath -Recurse -File | Where-Object {
    $_.Extension -in @('.md', '.json', '.yaml', '.yml', '.ps1')
}

foreach ($file in $textFiles) {
    $content = Get-Content -LiteralPath $file.FullName -Raw

    $skipAbsolutePathSelfCheck = $file.Name -eq 'validate-skill.ps1'

    if ((-not $skipAbsolutePathSelfCheck) -and $content -match '(?<!\\)C:\\Users\\|/Users/|/home/') {
        Add-WarningLine $warnings "Potential machine-specific absolute path found in $($file.FullName)"
    }

    $linkMatches = [regex]::Matches($content, '\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)')

    foreach ($match in $linkMatches) {
        $target = $match.Groups[1].Value.Trim()

        if ($target -match '^(https?:|mailto:|file:)' ) {
            continue
        }

        if ([System.IO.Path]::IsPathRooted($target)) {
            Add-WarningLine $warnings "Absolute local link found in $($file.FullName): $target"
            continue
        }

        $resolvedTarget = Join-Path $file.DirectoryName $target

        if (-not (Test-Path -LiteralPath $resolvedTarget)) {
            Add-ErrorLine $errors "Broken relative link in $($file.FullName): $target"
        }
    }
}

Write-Host "Validation target: $resolvedSkillPath"

if ($warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "Warnings:"
    foreach ($warning in $warnings) {
        Write-Host "- $warning"
    }
}

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "Errors:"
    foreach ($errorLine in $errors) {
        Write-Host "- $errorLine"
    }

    Write-Host ""
    Write-Host "Result: FAILED"
    exit 1
}

Write-Host ""
Write-Host "Result: PASSED"
exit 0
