param(
  [string]$Target = "$HOME/.config/opencode"
)

$source = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Test-Path $Target)) {
  New-Item -ItemType Directory -Path $Target | Out-Null
}

$items = @(
  "opencode.jsonc",
  "GLOBAL.md",
  "agents",
  "skills",
  "standards"
)

foreach ($item in $items) {
  $from = Join-Path $source $item
  $to = Join-Path $Target $item

  if (Test-Path $to) {
    Remove-Item -Recurse -Force $to
  }

  Copy-Item -Recurse -Force $from $to
}

Write-Host "Installed opencode ecosystem to $Target"
Write-Host "Restart opencode to load the new config."
