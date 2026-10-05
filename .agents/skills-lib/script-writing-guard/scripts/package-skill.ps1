param(
    [string]$SkillPath = (Join-Path $PSScriptRoot '..'),
    [string]$OutputDir
)

$ErrorActionPreference = 'Stop'

$resolvedSkillPath = (Resolve-Path -LiteralPath $SkillPath).Path
$skillDir = Get-Item -LiteralPath $resolvedSkillPath

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $skillDir.Parent.FullName '.dist'
}

$validateScript = Join-Path $PSScriptRoot 'validate-skill.ps1'

& $validateScript -SkillPath $resolvedSkillPath
if ($LASTEXITCODE -ne 0) {
    throw "Validation failed. Packaging stopped."
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$tempZip = Join-Path ([System.IO.Path]::GetTempPath()) ("{0}-{1}.zip" -f $skillDir.Name, [guid]::NewGuid().ToString('N'))
$packagePath = Join-Path $OutputDir ("{0}.skill" -f $skillDir.Name)

if (Test-Path -LiteralPath $tempZip) {
    Remove-Item -LiteralPath $tempZip -Force
}

if (Test-Path -LiteralPath $packagePath) {
    Remove-Item -LiteralPath $packagePath -Force
}

Compress-Archive -LiteralPath $resolvedSkillPath -DestinationPath $tempZip -CompressionLevel Optimal
Move-Item -LiteralPath $tempZip -Destination $packagePath

Write-Host "Packaged skill:"
Write-Host $packagePath
