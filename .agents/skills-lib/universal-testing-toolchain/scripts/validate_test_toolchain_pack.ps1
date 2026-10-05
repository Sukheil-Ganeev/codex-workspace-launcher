param(
  [string]$SkillRoot = (Split-Path -Parent $PSScriptRoot)
)

$required = @(
  'SKILL.md',
  'agents\openai.yaml',
  'references\tool-candidate-matrix.md',
  'references\project-type-routing.md'
)

$missing = @()
foreach ($item in $required) {
  $path = Join-Path $SkillRoot $item
  if (-not (Test-Path -LiteralPath $path)) {
    $missing += $item
  }
}

$result = [ordered]@{
  skill_root = $SkillRoot
  required_count = $required.Count
  missing_count = $missing.Count
  missing = $missing
  status = if ($missing.Count -eq 0) { 'PASS' } else { 'FAIL' }
}

$json = $result | ConvertTo-Json -Depth 4
$jsonPath = Join-Path $SkillRoot 'TEST_TOOLCHAIN_PACK_VERIFY.json'
$mdPath = Join-Path $SkillRoot 'TEST_TOOLCHAIN_PACK_VERIFY.md'

$json | Set-Content -LiteralPath $jsonPath -Encoding UTF8
@(
  '# Universal Testing Toolchain Verification'
  ''
  "- Status: $($result.status)"
  "- Required files: $($result.required_count)"
  "- Missing files: $($result.missing_count)"
  "- JSON: $jsonPath"
) | Set-Content -LiteralPath $mdPath -Encoding UTF8

Write-Output $json
if ($missing.Count -gt 0) { exit 1 }
