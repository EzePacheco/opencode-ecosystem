# Changelog

All notable changes to this portable opencode setup are documented here.

## Unreleased

- Re-centered the repo around native OpenCode as the primary runtime for a
  Neovide + OpenCode workflow, while keeping `codex/` as a reference harness.
- Fixed native installers so OpenCode runtime `AGENTS.md` now comes from
  `GLOBAL.md` instead of the repo-maintainer `AGENTS.md` file.
- Added native OpenCode `spec` and `architecture-decision` skills.
- Added native OpenCode `architecture-reviewer` and `security-reviewer`
  subagents.
- Upgraded the native OpenCode model matrix to the approved baseline: GPT-5.5
  for mentor/plan/build/review/reconcile/verifier/builders, GPT-5.4 for docs,
  GPT-5.4 Mini for both `explore` and `explore-mini`, and GPT-5.4 Mini for the
  disabled native `memory-retriever` placeholder.
- Added a native `spec` workflow with `.opencode/specs/` as the default
  repo-local convention for persisted specs, while also documenting
  `.codex/specs/`, `.claude/specs/`, and `docs/specs/` as valid spec
  locations.
- Relaxed native Orc Plan from fully read-only to spec-only writes: it can now
  create or update workspace `*.spec.md` files in those documented spec
  locations while remaining unable to edit non-spec files or implement
  changes.
- Made the native Mentor profile friendlier for learning-oriented questions,
  with stronger guidance to explain fundamentals, include file paths, and avoid
  assuming full prior context.
- Added `doctor-opencode.sh` and `doctor-opencode.ps1` to validate that
  repo-managed native OpenCode install surfaces on Linux/macOS and Windows stay
  in sync with this repo source.
- Added a documented Neovide + OpenCode workflow under
  `docs/neovide-opencode-workflow.md`.
- Added a native Codex adaptation under `codex/`, including global `AGENTS.md`,
  custom agents, skills, shared standards, `agentMemory` MCP config, installer,
  and doctor script. The Codex flow uses one main thread by default: mentor-like
  conversational mode and Orc Plan behavior in `/plan`, without requiring
  `--profile`.
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
  it disabled by default unless users install or override the local binary;
  direct use remains denied to native agents, including `memory-retriever`,
  pending separate approval.
- Standardized both native `explore` and `explore-mini` as cheap read-only
  `openai/gpt-5.4-mini` profiles.
- Updated the model and temperature matrix across core profiles (`plan`,
  `build`, builders, `explore-mini`, `verifier`, `reconciler`, and
  `code-reviewer`) to the approved operational baseline.
- Added `documentation-writer` and `memory-retriever` subagents for
  docs-focused updates and repo-file-backed persistent-memory verification.
- Strengthened `code-reviewer` to remain explicitly strict and finding-first,
  with explicit focus on security, contract regressions, and missing verification
  before acceptance.
- Added/updated native OpenCode docs to match implemented V3 flow details: handoff
  contract fields (`size`, `mini`, `needs_qa`, `human_gate`, `reference_files`,
  `risk_flags`, `tech_lead_recommended`, `worktree_recommended`,
  `max_rework_iterations`), structured reviewer/reconciler/verifier JSON contracts,
  max-3 verifier/reconciler rework loop, Mini-SDD safety gating, optional
  `tech-lead` for L/XL, `human_gate` pause position, and worktree/MCP safety
  policy.

  Source evidence: `agents/plan.md`, `agents/build.md`,
  `agents/code-reviewer.md`, `agents/architecture-reviewer.md`,
  `agents/security-reviewer.md`, `agents/reconciler.md`, `agents/verifier.md`,
   `agents/qa-builder.md`, `agents/tech-lead.md`, `agents/worktree-manager.md`,
   `opencode.jsonc`, `standards/ai-workflow-standards.md`,
   `docs/neovide-opencode-workflow.md`, `README.md`.
