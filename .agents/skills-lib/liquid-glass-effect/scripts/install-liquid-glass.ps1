param(
  [Parameter(Mandatory=$true)]
  [string]$ProjectPath,

  [ValidateSet("samasante", "pallavag", "rdev", "h0rhay", "zakisheriff", "aslanon-vue", "callstack-rn")]
  [string]$Provider = "samasante",

  [ValidateSet("auto", "npm", "pnpm", "yarn", "bun")]
  [string]$PackageManager = "auto",

  [switch]$InstallPeers,

  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$resolved = Resolve-Path -LiteralPath $ProjectPath
$project = $resolved.Path
$packageJson = Join-Path $project "package.json"

if (-not (Test-Path -LiteralPath $packageJson)) {
  throw "package.json not found in $project"
}

function Test-CommandExists($name) {
  $null -ne (Get-Command $name -ErrorAction SilentlyContinue)
}

if ($PackageManager -eq "auto") {
  if (Test-Path -LiteralPath (Join-Path $project "pnpm-lock.yaml")) {
    $PackageManager = "pnpm"
  } elseif (Test-Path -LiteralPath (Join-Path $project "yarn.lock")) {
    $PackageManager = "yarn"
  } elseif ((Test-Path -LiteralPath (Join-Path $project "bun.lock")) -or (Test-Path -LiteralPath (Join-Path $project "bun.lockb"))) {
    $PackageManager = "bun"
  } else {
    $PackageManager = "npm"
  }
}

$pkg = Get-Content -LiteralPath $packageJson -Raw | ConvertFrom-Json
$deps = @{}
if ($pkg.dependencies) {
  $pkg.dependencies.PSObject.Properties | ForEach-Object { $deps[$_.Name] = $_.Value }
}
if ($pkg.devDependencies) {
  $pkg.devDependencies.PSObject.Properties | ForEach-Object { $deps[$_.Name] = $_.Value }
}

$providerMap = @{
  "samasante"   = @{ Package = "@samasante/liquid-glass";       Peers = @("react", "react-dom"); Note = "Default React live-DOM/headless glass choice." }
  "pallavag"    = @{ Package = "liquid-glass-web-react";        Peers = @("react", "react-dom"); Note = "React live-DOM lens alternative; young package." }
  "rdev"        = @{ Package = "liquid-glass-react";            Peers = @("react", "react-dom"); Note = "React component with strong visual controls; currently expects React 19+." }
  "h0rhay"      = @{ Package = "liquid-glass-component-kit";    Peers = @();                     Note = "Vanilla JS first, optional React hook." }
  "zakisheriff" = @{ Package = "@zakisheriff/liquid-glass";     Peers = @("react", "react-dom"); Note = "Ready-made React UI components and shared CSS." }
  "aslanon-vue" = @{ Package = "@aslanonur/liquid-glass-vue";   Peers = @("vue");                Note = "Vue 3 / Nuxt 3 liquid glass component." }
  "callstack-rn"= @{ Package = "@callstack/liquid-glass";       Peers = @("react", "react-native"); Note = "React Native iOS route; not for web, requires native build constraints." }
}

$selected = $providerMap[$Provider]
if (-not $selected) {
  throw "Unknown provider: $Provider"
}

$missingPeers = @()
foreach ($peer in $selected.Peers) {
  if (-not $deps.ContainsKey($peer)) { $missingPeers += $peer }
}

$packages = @($selected.Package)
if ($InstallPeers -and $missingPeers.Count -gt 0) {
  $packages += $missingPeers
}

if ($missingPeers.Count -gt 0 -and -not $InstallPeers) {
  Write-Warning "Missing peer deps: $($missingPeers -join ', '). Re-run with -InstallPeers only if this project is meant for provider '$Provider'."
}
Write-Output "Provider: $Provider"
Write-Output "Package: $($selected.Package)"
Write-Output "Note: $($selected.Note)"
Write-Output "Package manager: $PackageManager"
Write-Output "Packages: $($packages -join ', ')"

if ($DryRun) {
  Write-Output "Dry run only. No package was installed."
  exit 0
}

if (-not (Test-CommandExists $PackageManager)) {
  throw "$PackageManager command not found"
}

Push-Location -LiteralPath $project
try {
  switch ($PackageManager) {
    "pnpm" { & pnpm add @packages }
    "yarn" { & yarn add @packages }
    "bun" { & bun add @packages }
    "npm" { & npm install @packages }
    default { throw "Unsupported package manager: $PackageManager" }
  }
  if ($LASTEXITCODE -ne 0) {
    throw "$PackageManager install failed with exit code $LASTEXITCODE"
  }
} finally {
  Pop-Location
}

Write-Output "Installed $($selected.Package) in $project using $PackageManager"
