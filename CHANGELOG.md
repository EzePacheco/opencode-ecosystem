# Changelog

All notable changes to this portable opencode setup are documented here.

## Unreleased

- Expanded the Mentor profile to reason from software-design fundamentals,
  compare patterns and alternatives explicitly, and use ask-gated web research
  with official-docs-first guidance and sanitized external queries.
- Added mentoring-oriented standards for software-design fundamentals, pattern
  selection, repository organization, technology decisions, and technical
  research guardrails.
- Added explicit reasoning variants to agent profiles based on current opencode model variant support.
- Updated Plan/Build role labels to Orc Plan and Del Build while keeping stable agent ids.
- Added a Bash installer for Linux/macOS alongside the existing PowerShell installer.
- Added an ask-mode mentor profile for standards-backed technical guidance without file edits.
- Updated builder and verifier model selections in agent configuration.
- Simplified the public README to keep operational details high level.
- Added hardening for portable/global installation: switched global instructions to
  `AGENTS.md`, added `AGENTS.md` source for portability, and hardened both
  installers (preflight checks, source/target guardrails, safer overwrite with
  backups, and stale-surface warnings).
- Fixed Bash default config target to prefer `$XDG_CONFIG_HOME` and added explicit
  PowerShell fail-closed + literal-path handling.
- Hardened agent task permissions so read-only profiles cannot delegate to
  write-capable subagents, while preserving Del Build delegation flow.
- Allowed code-reviewer read-only git inspection commands while denying other
  bash commands.
- Tightened Bash and PowerShell installer source/target overlap guards, root
  target rejection, `-- <target>` Bash parsing, and stale active-surface warnings.
- Added `GLOBAL.md` to managed installer items so legacy global instructions are
  refreshed with backup semantics.
- Declared the local `agent-memory` MCP server for persistent memory, but kept
  it disabled by default unless users install or override the local binary; direct
  use remains denied to standard agents so retrieval flows through
  `memory-retriever` via orchestration.
- Overrode the `explore` subagent with a cheap read-only DeepSeek profile and
  added `explore-mini` as an `openai/gpt-5.4-mini` fallback when DeepSeek is
  unavailable or fails.
- Updated the model and temperature matrix across core profiles (`plan`,
  `build`, builders, `explore-mini`, `verifier`, `reconciler`, and
  `code-reviewer`) to the approved operational baseline.
- Added `documentation-writer` and `memory-retriever` subagents for
  docs-focused updates and repo-file-backed persistent-memory verification.
- Strengthened `code-reviewer` to remain explicitly strict and finding-first,
  with explicit focus on security, contract regressions, and missing verification
  before acceptance.
