param(
  [string]$Target,
  [switch]$Help
)

$ErrorActionPreference = 'Stop'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Show-Usage {
@"
Usage: .\doctor-opencode.ps1 [-Target <path>]

Validates that the repo-managed native OpenCode install surfaces in the target
still match this repo source. This is not a general validator for arbitrary
custom localizations outside the managed surface set.
Defaults to $HOME/.config/opencode (or $env:XDG_CONFIG_HOME/opencode if set).
"@
}

if ($Help) {
  Write-Host (Show-Usage)
  exit 0
}

if ($PSVersionTable.PSVersion.Major -lt 7) {
  throw 'doctor-opencode.ps1 requires PowerShell 7+.'
}

$configRoot = if (-not [string]::IsNullOrWhiteSpace($env:XDG_CONFIG_HOME)) {
  $env:XDG_CONFIG_HOME
} else {
  Join-Path $HOME '.config'
}

if ([string]::IsNullOrWhiteSpace($Target)) {
  $Target = Join-Path $configRoot 'opencode'
}

$Target = [System.IO.Path]::GetFullPath($Target)
$fail = $false

function Check-File {
  param([string]$Path)
  if (Test-Path -LiteralPath $Path -PathType Leaf) {
    Write-Host "ok file  $Path"
  } else {
    Write-Host "missing  $Path"
    $script:fail = $true
  }
}

function Check-Dir {
  param([string]$Path)
  if (Test-Path -LiteralPath $Path -PathType Container) {
    Write-Host "ok dir   $Path"
  } else {
    Write-Host "missing  $Path"
    $script:fail = $true
  }
}

Check-File (Join-Path $Target 'opencode.jsonc')
Check-File (Join-Path $Target 'AGENTS.md')
Check-File (Join-Path $Target 'GLOBAL.md')
Check-Dir (Join-Path $Target 'agents')
Check-Dir (Join-Path $Target 'skills')
Check-Dir (Join-Path $Target 'standards')

foreach ($skill in @('workflow-sdd', 'spec', 'architecture-decision', 'adversarial-review', 'reconcile', 'ship-check')) {
  Check-File (Join-Path $Target "skills/$skill/SKILL.md")
}

foreach ($agent in @(
  'mentor', 'plan', 'build', 'backend-builder', 'frontend-builder',
  'database-builder', 'devops-builder', 'qa-builder', 'tech-lead', 'code-reviewer',
  'architecture-reviewer', 'security-reviewer', 'reconciler',
  'verifier', 'explore', 'explore-mini', 'worktree-manager', 'documentation-writer',
  'memory-retriever'
)) {
  Check-File (Join-Path $Target "agents/$agent.md")
}

if ($fail) {
  exit 1
}

$configPath = Join-Path $Target 'opencode.jsonc'
$jsonOptions = [System.Text.Json.JsonDocumentOptions]::new()
$jsonOptions.CommentHandling = [System.Text.Json.JsonCommentHandling]::Skip
$jsonOptions.AllowTrailingCommas = $true
$configDocument = [System.Text.Json.JsonDocument]::Parse((Get-Content -LiteralPath $configPath -Raw), $jsonOptions)
$config = $configDocument.RootElement

if ($config.GetProperty('$schema').GetString() -ne 'https://opencode.ai/config.json') { throw "unexpected `$schema" }
if ($config.GetProperty('model').GetString() -ne 'openai/gpt-5.5') { throw 'unexpected model' }
if ($config.GetProperty('small_model').GetString() -ne 'openai/gpt-5.4-mini') { throw 'unexpected small_model' }
if ($config.GetProperty('default_agent').GetString() -ne 'plan') { throw 'unexpected default_agent' }
if ($config.GetProperty('mcp').GetProperty('agent-memory').GetProperty('enabled').GetBoolean() -ne $false) { throw 'unexpected mcp.agent-memory.enabled' }
if ($config.GetProperty('permission').GetProperty('agent-memory_*').GetString() -ne 'deny') { throw 'missing permission agent-memory_* = deny' }
if ($config.GetProperty('references').GetProperty('standards').GetProperty('path').GetString() -ne './standards') { throw 'unexpected standards reference path' }

foreach ($forbiddenKey in @('approval_policy', 'plan_mode_reasoning_effort', 'web_search', 'sandbox_mode')) {
  $placeholder = [System.Text.Json.JsonElement]::new()
  if ($config.TryGetProperty($forbiddenKey, [ref]$placeholder)) {
    throw "unexpected Codex-only config key: $forbiddenKey"
  }
}

Write-Host 'ok json  opencode config validated'

$agentsPath = Join-Path $Target 'AGENTS.md'
$globalPath = Join-Path $Target 'GLOBAL.md'
$agentsText = Get-Content -LiteralPath $agentsPath -Raw
$globalText = Get-Content -LiteralPath $globalPath -Raw

foreach ($forbidden in @('doctor-codex', '~/.codex', 'codex/AGENTS.md', 'install-codex.sh')) {
  if ($agentsText.Contains($forbidden) -or $globalText.Contains($forbidden)) {
    throw "forbidden Codex runtime reference found: $forbidden"
  }
}

if ($agentsText -ne $globalText) {
  throw 'AGENTS.md and GLOBAL.md differ in installed target'
}
if ($globalText -ne (Get-Content -LiteralPath (Join-Path $ScriptRoot 'GLOBAL.md') -Raw)) {
  throw 'installed GLOBAL.md differs from repo source GLOBAL.md'
}

Write-Host 'ok docs  runtime instruction files validated'

$expected = @{
  'mentor' = @('openai/gpt-5.5', 'high', 'high')
  'plan' = @('openai/gpt-5.5', 'xhigh', 'high')
  'build' = @('openai/gpt-5.5', 'high', 'high')
  'backend-builder' = @('openai/gpt-5.5', 'medium', 'medium')
  'frontend-builder' = @('openai/gpt-5.5', 'medium', 'medium')
  'database-builder' = @('openai/gpt-5.5', 'medium', 'medium')
  'devops-builder' = @('openai/gpt-5.5', 'medium', 'medium')
  'qa-builder' = @('openai/gpt-5.5', 'high', 'high')
  'tech-lead' = @('openai/gpt-5.5', 'xhigh', 'high')
  'code-reviewer' = @('openai/gpt-5.5', 'xhigh', 'high')
  'architecture-reviewer' = @('openai/gpt-5.5', 'high', 'high')
  'security-reviewer' = @('openai/gpt-5.5', 'high', 'high')
  'reconciler' = @('openai/gpt-5.5', 'high', 'high')
  'verifier' = @('openai/gpt-5.5', 'high', 'high')
  'explore' = @('openai/gpt-5.4-mini', 'medium', 'medium')
  'explore-mini' = @('openai/gpt-5.4-mini', 'medium', 'medium')
  'worktree-manager' = @('openai/gpt-5.4-mini', 'medium', 'medium')
  'documentation-writer' = @('openai/gpt-5.4', 'medium', 'medium')
  'memory-retriever' = @('openai/gpt-5.4-mini', 'medium', 'medium')
}

foreach ($name in $expected.Keys) {
  $text = Get-Content -LiteralPath (Join-Path $Target "agents/$name.md") -Raw
  $modelMatch = [regex]::Match($text, '^model:\s*(.+)$', [System.Text.RegularExpressions.RegexOptions]::Multiline)
  $variantMatch = [regex]::Match($text, '^variant:\s*(.+)$', [System.Text.RegularExpressions.RegexOptions]::Multiline)
  $reasoningEffortMatch = [regex]::Match($text, '^reasoningEffort:\s*(.+)$', [System.Text.RegularExpressions.RegexOptions]::Multiline)
  $actual = @($modelMatch.Groups[1].Value.Trim(), $variantMatch.Groups[1].Value.Trim(), $reasoningEffortMatch.Groups[1].Value.Trim())
  $expectedPair = $expected[$name]
  if ($variantMatch.Success -and -not $reasoningEffortMatch.Success) {
    throw "$name has variant without corresponding reasoningEffort"
  }
  if ($actual[0] -ne $expectedPair[0] -or $actual[1] -ne $expectedPair[1] -or $actual[2] -ne $expectedPair[2]) {
    throw "unexpected $name: $($actual -join ', '), expected $($expectedPair -join ', ')"
  }
}

$planText = Get-Content -LiteralPath (Join-Path $Target 'agents/plan.md') -Raw
if ($planText.Contains('edit: allow')) {
  throw 'plan agent must not have broad edit allow'
}
$frontMatterMatch = [regex]::Match(
  $planText,
  '^---\r?\n(?<body>.*?)(?:\r?\n)---(?:\r?\n|$)',
  [System.Text.RegularExpressions.RegexOptions]::Singleline
)
if (-not $frontMatterMatch.Success) {
  throw 'plan agent missing front matter'
}
$frontMatterLines = $frontMatterMatch.Groups['body'].Value -split "`r?`n"

function Get-NestedBlockLines {
  param(
    [string[]]$Lines,
    [string]$Header,
    [string]$ChildPrefix
  )

  $index = [Array]::IndexOf($Lines, $Header)
  if ($index -lt 0) {
    return $null
  }

  $block = New-Object System.Collections.Generic.List[string]
  for ($i = $index + 1; $i -lt $Lines.Count; $i++) {
    $line = $Lines[$i]
    if (-not $line.StartsWith($ChildPrefix)) {
      break
    }
    $block.Add($line)
  }

  return $block.ToArray()
}

$permissionLines = Get-NestedBlockLines -Lines $frontMatterLines -Header 'permission:' -ChildPrefix '  '
if ($null -eq $permissionLines) {
  throw 'plan agent missing permission block'
}

$editLines = Get-NestedBlockLines -Lines $permissionLines -Header '  edit:' -ChildPrefix '    '
$expectedEditLines = @(
  '    "*": deny',
  '    ".opencode/specs/*.spec.md": allow',
  '    ".opencode/specs/**/*.spec.md": allow',
  '    ".codex/specs/*.spec.md": allow',
  '    ".codex/specs/**/*.spec.md": allow',
  '    ".claude/specs/*.spec.md": allow',
  '    ".claude/specs/**/*.spec.md": allow',
  '    "docs/specs/*.spec.md": allow',
  '    "docs/specs/**/*.spec.md": allow',
  '    "*.spec.md": allow',
  '    "**/*.spec.md": allow'
)
if ($null -eq $editLines -or $editLines.Count -ne $expectedEditLines.Count) {
  throw 'plan agent edit permissions differ from expected spec-only block'
}
for ($i = 0; $i -lt $expectedEditLines.Count; $i++) {
  if ($editLines[$i] -ne $expectedEditLines[$i]) {
    throw 'plan agent edit permissions differ from expected spec-only block'
  }
}
if (-not ($permissionLines -contains '  bash: deny')) {
  throw 'plan agent missing bash deny in permission block'
}
foreach ($required in @('task:', 'explore: allow', 'explore-mini: allow', 'architecture-reviewer: allow', 'security-reviewer: allow')) {
  if (-not $planText.Contains($required)) {
    throw "plan agent missing spec-only safeguard: $required"
  }
}
foreach ($forbidden in @('    code-reviewer: allow', '    memory-retriever: allow')) {
  if ($permissionLines -contains $forbidden) {
    throw "plan agent has forbidden delegation permission: $($forbidden.Trim())"
  }
}
foreach ($required in @('max_rework_iterations: 3', 'allowed_test_paths', 'verification_commands', '`agents`, `workflow runtime`, `worktree orchestration`, `public contracts`,', '`permissions`, `MCP`, `agent-memory`, `auth`, `secrets`, `privacy`,', 'require both reviewers.')) {
  if (-not $planText.Contains($required)) {
    throw "plan agent missing V3 risk or QA contract: $required"
  }
}

$mentorText = Get-Content -LiteralPath (Join-Path $Target 'agents/mentor.md') -Raw
foreach ($required in @('architecture-reviewer: allow', 'security-reviewer: allow')) {
  if (-not $mentorText.Contains($required)) {
    throw "mentor agent missing reviewer delegation permission: $required"
  }
}

foreach ($reviewer in @('architecture-reviewer', 'security-reviewer')) {
  $text = Get-Content -LiteralPath (Join-Path $Target "agents/$reviewer.md") -Raw
  foreach ($required in @(
    '"git status --short": allow',
    '"git diff": allow',
    '"git diff --stat": allow',
    '"git log --oneline -10": allow',
    '"git show --stat": allow'
  )) {
    if (-not $text.Contains($required)) {
      throw "$reviewer missing git inspection permission: $required"
    }
  }
}

$worktreeText = Get-Content -LiteralPath (Join-Path $Target 'agents/worktree-manager.md') -Raw
foreach ($required in @(
  '"git worktree list": allow',
  '"git worktree add": allow',
  '"git status --short": allow',
  'Do not run `git commit`, `git merge`, `git push`, `git reset`, `git rebase`,',
  'leave removal to the human instead of running it yourself.'
)) {
  if (-not $worktreeText.Contains($required)) {
    throw "worktree-manager missing safety requirement: $required"
  }
}
if ($worktreeText.Contains('"git worktree remove": allow')) {
  throw 'worktree-manager has forbidden destructive permission: "git worktree remove": allow'
}

$qaText = Get-Content -LiteralPath (Join-Path $Target 'agents/qa-builder.md') -Raw
foreach ($required in @(
  'Prefer Playwright for E2E coverage only when the project already supports it',
  'files_changed;',
  'tests_added;',
  'commands_run;',
  'failures;',
  'residual_risk.'
)) {
  if (-not $qaText.Contains($required)) {
    throw "qa-builder missing contract requirement: $required"
  }
}

$buildText = Get-Content -LiteralPath (Join-Path $Target 'agents/build.md') -Raw
foreach ($required in @(
  'QA handoff fields required when `needs_qa=true`:',
  '`spec`',
  '`reference_files`',
  '`allowed_test_paths`',
  '`verification_commands`',
  'Capture the returned `worktrees_touched` paths and assign at most one',
  'Cleanup is report-only:',
  '`agents`, `workflow runtime`, `worktree orchestration`, `public contracts`,',
  '`permissions`, `MCP`, `agent-memory`, `auth`, `secrets`, `privacy`,',
  'Count each `reconciler -> verifier` retry as one rework iteration.'
)) {
  if (-not $buildText.Contains($required)) {
    throw "build agent missing V3 contract requirement: $required"
  }
}

foreach ($reviewer in @('code-reviewer', 'architecture-reviewer', 'security-reviewer')) {
  $text = Get-Content -LiteralPath (Join-Path $Target "agents/$reviewer.md") -Raw
  foreach ($required in @('"verdict": "accepted | rework-required"', '"findings": [', '"open_questions": [],', '"verification_gaps": []')) {
    if (-not $text.Contains($required)) {
      throw "$reviewer missing common findings schema key: $required"
    }
  }
}
if ((Get-Content -LiteralPath (Join-Path $Target 'agents/architecture-reviewer.md') -Raw).Contains('"alternatives": []')) {
  throw 'architecture-reviewer still documents schema extension key: "alternatives": []'
}
if ((Get-Content -LiteralPath (Join-Path $Target 'agents/security-reviewer.md') -Raw).Contains('"residual_risk": []')) {
  throw 'security-reviewer still documents schema extension key: "residual_risk": []'
}

$memoryText = Get-Content -LiteralPath (Join-Path $Target 'agents/memory-retriever.md') -Raw
foreach ($required in @('"agent-memory_*": deny', 'remains disabled and denied pending separate approval', 'Do not invoke `agent-memory` or any other persistent-memory MCP.')) {
  if (-not $memoryText.Contains($required)) {
    throw "memory-retriever missing native memory safeguard: $required"
  }
}

Write-Host 'ok docs  agent matrix and plan permissions validated'

$compareList = @(
  @{ Source = (Join-Path $ScriptRoot 'opencode.jsonc'); Destination = (Join-Path $Target 'opencode.jsonc') },
  @{ Source = (Join-Path $ScriptRoot 'GLOBAL.md'); Destination = (Join-Path $Target 'GLOBAL.md') },
  @{ Source = (Join-Path $ScriptRoot 'GLOBAL.md'); Destination = (Join-Path $Target 'AGENTS.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/INDEX.md'); Destination = (Join-Path $Target 'standards/INDEX.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/engineering-principles.md'); Destination = (Join-Path $Target 'standards/engineering-principles.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/software-design-fundamentals.md'); Destination = (Join-Path $Target 'standards/software-design-fundamentals.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/patterns-catalog.md'); Destination = (Join-Path $Target 'standards/patterns-catalog.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/repository-organization-standards.md'); Destination = (Join-Path $Target 'standards/repository-organization-standards.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/technology-decision-playbook.md'); Destination = (Join-Path $Target 'standards/technology-decision-playbook.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/technical-research-standards.md'); Destination = (Join-Path $Target 'standards/technical-research-standards.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/architecture-decision-standards.md'); Destination = (Join-Path $Target 'standards/architecture-decision-standards.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/development-methodologies.md'); Destination = (Join-Path $Target 'standards/development-methodologies.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/testing-standards.md'); Destination = (Join-Path $Target 'standards/testing-standards.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/security-engineering-standards.md'); Destination = (Join-Path $Target 'standards/security-engineering-standards.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/backend-architecture-standards.md'); Destination = (Join-Path $Target 'standards/backend-architecture-standards.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/api-contract-standards.md'); Destination = (Join-Path $Target 'standards/api-contract-standards.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/database-architecture-standards.md'); Destination = (Join-Path $Target 'standards/database-architecture-standards.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/frontend-architecture-standards.md'); Destination = (Join-Path $Target 'standards/frontend-architecture-standards.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/distributed-systems-standards.md'); Destination = (Join-Path $Target 'standards/distributed-systems-standards.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/operability-standards.md'); Destination = (Join-Path $Target 'standards/operability-standards.md') },
  @{ Source = (Join-Path $ScriptRoot 'standards/ai-workflow-standards.md'); Destination = (Join-Path $Target 'standards/ai-workflow-standards.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/mentor.md'); Destination = (Join-Path $Target 'agents/mentor.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/plan.md'); Destination = (Join-Path $Target 'agents/plan.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/build.md'); Destination = (Join-Path $Target 'agents/build.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/backend-builder.md'); Destination = (Join-Path $Target 'agents/backend-builder.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/frontend-builder.md'); Destination = (Join-Path $Target 'agents/frontend-builder.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/database-builder.md'); Destination = (Join-Path $Target 'agents/database-builder.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/devops-builder.md'); Destination = (Join-Path $Target 'agents/devops-builder.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/qa-builder.md'); Destination = (Join-Path $Target 'agents/qa-builder.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/tech-lead.md'); Destination = (Join-Path $Target 'agents/tech-lead.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/code-reviewer.md'); Destination = (Join-Path $Target 'agents/code-reviewer.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/architecture-reviewer.md'); Destination = (Join-Path $Target 'agents/architecture-reviewer.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/security-reviewer.md'); Destination = (Join-Path $Target 'agents/security-reviewer.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/reconciler.md'); Destination = (Join-Path $Target 'agents/reconciler.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/verifier.md'); Destination = (Join-Path $Target 'agents/verifier.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/explore.md'); Destination = (Join-Path $Target 'agents/explore.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/explore-mini.md'); Destination = (Join-Path $Target 'agents/explore-mini.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/worktree-manager.md'); Destination = (Join-Path $Target 'agents/worktree-manager.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/documentation-writer.md'); Destination = (Join-Path $Target 'agents/documentation-writer.md') },
  @{ Source = (Join-Path $ScriptRoot 'agents/memory-retriever.md'); Destination = (Join-Path $Target 'agents/memory-retriever.md') },
  @{ Source = (Join-Path $ScriptRoot 'skills/workflow-sdd/SKILL.md'); Destination = (Join-Path $Target 'skills/workflow-sdd/SKILL.md') },
  @{ Source = (Join-Path $ScriptRoot 'skills/spec/SKILL.md'); Destination = (Join-Path $Target 'skills/spec/SKILL.md') },
  @{ Source = (Join-Path $ScriptRoot 'skills/architecture-decision/SKILL.md'); Destination = (Join-Path $Target 'skills/architecture-decision/SKILL.md') },
  @{ Source = (Join-Path $ScriptRoot 'skills/adversarial-review/SKILL.md'); Destination = (Join-Path $Target 'skills/adversarial-review/SKILL.md') },
  @{ Source = (Join-Path $ScriptRoot 'skills/reconcile/SKILL.md'); Destination = (Join-Path $Target 'skills/reconcile/SKILL.md') },
  @{ Source = (Join-Path $ScriptRoot 'skills/ship-check/SKILL.md'); Destination = (Join-Path $Target 'skills/ship-check/SKILL.md') }
)

foreach ($pair in $compareList) {
  $sourceText = Get-Content -LiteralPath $pair.Source -Raw
  $destinationText = Get-Content -LiteralPath $pair.Destination -Raw
  if ($sourceText -ne $destinationText) {
    throw "installed file differs from repo source: $($pair.Destination)"
  }
}

Write-Host 'ok docs  installed files match repo source for managed root surfaces and standards'

if ($fail) {
  exit 1
}
