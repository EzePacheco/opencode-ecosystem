param(
  [string]$Target,
  [switch]$Force,
  [switch]$Help
)

$ErrorActionPreference = 'Stop'

function Show-Usage {
@"
Usage: .\install.ps1 [-Target <path>] [-Force]

Installs the portable opencode setup into the target directory.

Defaults:
  - Target defaults to $HOME/.config/opencode (or $env:XDG_CONFIG_HOME/opencode if set)
  - existing managed items are backed up before overwrite unless -Force is set

Examples:
  .\install.ps1
  .\install.ps1 -Target "$HOME/.config/opencode"
  .\install.ps1 -Target "$HOME/.config/opencode" -Force
"@
}

if ($Help) {
  Write-Host (Show-Usage)
  exit 0
}

function Normalize-ComparablePath {
  param([Parameter(Mandatory = $true)][string]$Path)

  $full = [System.IO.Path]::GetFullPath($Path)
  $root = [System.IO.Path]::GetPathRoot($full)
  if ($full.Length -gt $root.Length) {
    $full = $full.TrimEnd(@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar))
  }
  return $full
}

function Test-SameOrChildPath {
  param(
    [Parameter(Mandatory = $true)][string]$Candidate,
    [Parameter(Mandatory = $true)][string]$Parent
  )

  $candidateFull = Normalize-ComparablePath -Path $Candidate
  $parentFull = Normalize-ComparablePath -Path $Parent
  if ([string]::Equals($candidateFull, $parentFull, [System.StringComparison]::OrdinalIgnoreCase)) {
    return $true
  }

  $parentWithSeparator = $parentFull.TrimEnd(@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)) + [System.IO.Path]::DirectorySeparatorChar
  return $candidateFull.StartsWith($parentWithSeparator, [System.StringComparison]::OrdinalIgnoreCase)
}

function Resolve-ExistingPhysicalPath {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [switch]$RejectReparse
  )

  if ($RejectReparse) {
    Assert-NoExistingReparseInPath -Path $Path
  }

  $resolved = Resolve-Path -LiteralPath $Path -ErrorAction Stop
  return [System.IO.Path]::GetFullPath($resolved.ProviderPath)
}

function Resolve-PhysicalPathBestEffort {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [switch]$RejectReparse
  )

  $full = [System.IO.Path]::GetFullPath($Path)
  if ($RejectReparse) {
    Assert-NoExistingReparseInPath -Path $full
  }

  if (Test-VisiblePathExists -Path $full) {
    return Resolve-ExistingPhysicalPath -Path $full -RejectReparse:$RejectReparse
  }

  $missing = [System.Collections.Generic.List[string]]::new()
  $probe = $full
  while (-not (Test-VisiblePathExists -Path $probe)) {
    $leaf = Split-Path -Leaf $probe
    if ([string]::IsNullOrEmpty($leaf)) {
      throw "Cannot resolve path ancestor: $full"
    }
    $missing.Insert(0, $leaf)
    $parent = Split-Path -Parent $probe
    if ([string]::IsNullOrEmpty($parent) -or $parent -eq $probe) {
      throw "Cannot resolve path ancestor: $full"
    }
    $probe = $parent
  }

  $ancestorItem = Get-ExistingItem -Path $probe
  if ($null -eq $ancestorItem) {
    throw "Cannot resolve path ancestor: $full"
  }
  if ($RejectReparse) {
    Assert-ItemIsNotReparsePoint -Item $ancestorItem -Path $probe
  }
  if (-not $ancestorItem.PSIsContainer) {
    throw "Nearest existing target ancestor is not a directory: $probe"
  }

  $resolved = Resolve-ExistingPhysicalPath -Path $probe -RejectReparse:$RejectReparse
  foreach ($part in $missing) {
    $resolved = Join-Path -Path $resolved -ChildPath $part
  }
  return [System.IO.Path]::GetFullPath($resolved)
}

function Get-ExistingItem {
  param([Parameter(Mandatory = $true)][string]$Path)

  try {
    return Get-Item -LiteralPath $Path -Force -ErrorAction Stop
  } catch {
    if ($_.CategoryInfo.Category -eq [System.Management.Automation.ErrorCategory]::ObjectNotFound) {
      return $null
    }
    throw
  }
}

function Test-VisiblePathExists {
  param([Parameter(Mandatory = $true)][string]$Path)

  return $null -ne (Get-ExistingItem -Path $Path)
}

function Assert-ItemIsNotReparsePoint {
  param(
    [Parameter(Mandatory = $true)]$Item,
    [Parameter(Mandatory = $true)][string]$Path
  )

  if (($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw "Refusing to use reparse point in install path: $Path"
  }
}

function Assert-NoExistingReparseInPath {
  param([Parameter(Mandatory = $true)][string]$Path)

  $probe = [System.IO.Path]::GetFullPath($Path)
  while ($true) {
    $item = Get-ExistingItem -Path $probe
    if ($null -ne $item) {
      Assert-ItemIsNotReparsePoint -Item $item -Path $probe
    }

    $parent = Split-Path -Parent $probe
    if ([string]::IsNullOrEmpty($parent) -or $parent -eq $probe) {
      break
    }
    $probe = $parent
  }
}

function Assert-NoSourceTargetOverlap {
  param(
    [Parameter(Mandatory = $true)][string]$Candidate,
    [Parameter(Mandatory = $true)][string]$SourceRoot
  )

  if (Test-SameOrChildPath -Candidate $Candidate -Parent $SourceRoot) {
    throw "Refusing to install into source tree: $Candidate"
  }
  if (Test-SameOrChildPath -Candidate $SourceRoot -Parent $Candidate) {
    throw "Refusing to install into a target that contains the source tree: $Candidate"
  }
}

function Assert-SafeDestination {
  param(
    [Parameter(Mandatory = $true)][string]$Destination,
    [Parameter(Mandatory = $true)][string]$TargetRoot,
    [Parameter(Mandatory = $true)][string]$SourceRoot
  )

  $destinationFull = Resolve-PhysicalPathBestEffort -Path $Destination -RejectReparse
  if (-not (Test-SameOrChildPath -Candidate $destinationFull -Parent $TargetRoot)) {
    throw "Refusing destination outside target: $destinationFull"
  }
  Assert-NoSourceTargetOverlap -Candidate $destinationFull -SourceRoot $SourceRoot
}

$configRoot = if (-not [string]::IsNullOrWhiteSpace($env:XDG_CONFIG_HOME)) {
  $env:XDG_CONFIG_HOME
} else {
  Join-Path $HOME '.config'
}

if ([string]::IsNullOrWhiteSpace($Target)) {
  $Target = Join-Path $configRoot 'opencode'
}

$source = Resolve-PhysicalPathBestEffort -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)
$targetFull = Resolve-PhysicalPathBestEffort -Path $Target -RejectReparse
$targetRoot = [System.IO.Path]::GetPathRoot($targetFull)

if ([string]::Equals((Normalize-ComparablePath -Path $targetFull), (Normalize-ComparablePath -Path $targetRoot), [System.StringComparison]::OrdinalIgnoreCase)) {
  throw "Refusing to install into filesystem root: $targetFull"
}

Assert-NoSourceTargetOverlap -Candidate $targetFull -SourceRoot $source

if (Test-VisiblePathExists -Path $targetFull) {
  $targetItem = Get-ExistingItem -Path $targetFull
  if (-not $targetItem.PSIsContainer) {
    throw "Target exists but is not a directory: $targetFull"
  }
}

$items = @(
  'opencode.jsonc',
  'AGENTS.md',
  'GLOBAL.md',
  'agents',
  'skills',
  'standards'
)

foreach ($item in $items) {
  $from = Join-Path -Path $source -ChildPath $item
  if (-not (Test-VisiblePathExists -Path $from)) {
    throw "Missing source item: $from"
  }
}

if (-not (Test-VisiblePathExists -Path $targetFull)) {
  [System.IO.Directory]::CreateDirectory($targetFull) | Out-Null
}

$Target = Resolve-PhysicalPathBestEffort -Path $targetFull -RejectReparse

$staleItems = @(
  'opencode.json',
  'config.json',
  'commands',
  'plugins',
  'modes',
  'agent',
  'skill'
)

foreach ($stale in $staleItems) {
  $stalePath = Join-Path -Path $Target -ChildPath $stale
  if (Test-VisiblePathExists -Path $stalePath) {
    Write-Warning "Existing opencode surface kept untouched and may still be loaded/merged by opencode: $stalePath"
  }
}

Write-Host "Managed items will be replaced in $Target: $($items -join ', ')"

if ($Force) {
  Write-Host 'Overwrite mode: -Force active, replacements will not be backed up.'
} else {
  Write-Host 'Safe mode: existing managed items will be moved to a timestamped backup before replacement.'
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$timestamp = "$timestamp-$PID"
$backupRoot = Join-Path -Path $Target -ChildPath '.opencode-install-backup'
$backupRoot = Join-Path -Path $backupRoot -ChildPath $timestamp

foreach ($item in $items) {
  $from = Join-Path -Path $source -ChildPath $item
  $to = Join-Path -Path $Target -ChildPath $item
  Assert-SafeDestination -Destination $to -TargetRoot $Target -SourceRoot $source

  if (Test-VisiblePathExists -Path $to) {
    if ($Force) {
      Remove-Item -Recurse -Force -LiteralPath $to
    } else {
      $backup = Join-Path -Path $backupRoot -ChildPath $item
      Assert-SafeDestination -Destination $backup -TargetRoot $Target -SourceRoot $source
      $backupDir = Split-Path -Parent $backup
      if (-not (Test-VisiblePathExists -Path $backupDir)) {
        [System.IO.Directory]::CreateDirectory($backupDir) | Out-Null
      }
      Move-Item -LiteralPath $to -Destination $backup -Force
      Write-Host "Backed up $to -> $backup"
    }
  }

  Copy-Item -Recurse -Force -LiteralPath $from -Destination $to
}

Write-Host "Installed opencode ecosystem to $Target"
Write-Host 'Restart opencode to load the new config.'
