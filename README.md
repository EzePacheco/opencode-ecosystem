# opencode-ecosystem

Portable opencode setup for spec-first development, implementation assistance,
review, reconciliation, verification, and standards-backed mentoring.

## Includes

- `opencode.jsonc`: portable global config.
- `GLOBAL.md`: short default instruction set.
- `agents/`: primary and subagent profiles for planning, implementation, review,
  verification, and mentoring.
- `skills/`: reusable workflows for planning, review, reconciliation, and final
  checks.
- `standards/`: curated technical standards and opencode workflow guidance.
- `install.ps1`: copies this repo into `~/.config/opencode` on Windows.
- `install.sh`: copies this repo into `~/.config/opencode` on Linux/macOS.

## Install On Another PC

1. Clone this repo.
2. Run the installer for your OS.

PowerShell on Windows:

```powershell
./install.ps1
```

Bash on Linux/macOS:

```bash
chmod +x ./install.sh
./install.sh
```

3. Restart opencode.

Default install target:

```text
~/.config/opencode
```

Custom target:

```powershell
./install.ps1 -Target "$HOME/.config/opencode"
```

```bash
./install.sh "$HOME/.config/opencode"
```

## Agent Profiles

This setup includes primary profiles for day-to-day orchestration, planning,
implementation flow, and ask-mode mentoring. It also includes scoped subagents
for backend, frontend, database, DevOps, review, reconciliation, and verification
tasks.

The public README intentionally stays high level. Inspect the files under
`agents/` for exact model selections, permissions, and profile instructions before
installing or customizing them.

## Workflow

Use the default Orc Plan profile for normal orchestration and specs before
implementation. Switch to the Del Build profile when scope is clear, and to the
Mentor profile when you want ask-mode guidance without file edits.

## Standards

Load standards on demand via the `standards` reference. Start with:

```text
@standards/INDEX.md
```

Do not load every standard by default.

## MCP Memory

This repo intentionally does not hardcode your project-memory MCP yet.

Add it later in `opencode.jsonc` once you have a portable command or remote URL.
Keep tokens and machine-specific secrets out of the repo. Prefer environment
variables or machine-local overrides.
