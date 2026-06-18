# Changelog

All notable changes to this portable opencode setup are documented here.

## Unreleased

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
- Added the local `agent-memory` MCP server configuration for persistent memory,
  disabled by default because the external memory binary is not bundled.
- Overrode the `explore` subagent with a cheap read-only DeepSeek profile and
  added `explore-mini` as an `openai/gpt-5.4-mini-fast` fallback because GPT-5.4
  Nano is not exposed by the current runtime; it can be switched to Nano when
  available.
