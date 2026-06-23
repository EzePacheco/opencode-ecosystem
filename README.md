# opencode-ecosystem

Portable opencode setup for spec-first development, implementation assistance,
review, reconciliation, verification, and standards-backed mentoring.

Primary working style: **Neovide + native OpenCode**.

## Includes

- `opencode.jsonc`: portable global config.
- `AGENTS.md`: repo guidance for this dual-surface repository.
- `GLOBAL.md`: canonical native OpenCode runtime instruction source; installers
  copy it into the target as both `AGENTS.md` and `GLOBAL.md`.
- `agents/`: primary and subagent profiles for planning, implementation, review,
  verification, and mentoring.
- `skills/`: reusable workflows for planning, spec creation, architecture
  decisions, review, reconciliation, and final checks.
- `standards/`: curated technical standards and opencode workflow guidance,
  including design fundamentals, patterns, repository organization, technology
  decision playbooks, and external research guardrails.
- `doctor-opencode.sh`: validates a native OpenCode install on Linux/macOS.
- `doctor-opencode.ps1`: validates a native OpenCode install on Windows.
- `install.ps1`: copies this repo into `~/.config/opencode` (or `$XDG_CONFIG_HOME` if set) on Windows.
- `install.sh`: copies this repo into `~/.config/opencode` (or `$XDG_CONFIG_HOME`) on Linux/macOS.
- `codex/`: native Codex adaptation using `~/.codex/AGENTS.md`, custom agents,
  user skills, shared standards, and `agent-memory` MCP.
- `install-codex.sh`: installs the native Codex adaptation on Linux/macOS.
- `doctor-codex.sh`: checks the native Codex adaptation after install.

## Install On Another PC

1. Clone this repo.
2. Run the installer for your OS.

PowerShell on Windows:

```powershell
./install.ps1
```

- Managed items are backed up before replacement by default, in a timestamped
  `.opencode-install-backup/<timestamp>/` directory inside the target.
- Use `-Force` to replace managed items without backup.
- Installers manage `opencode.jsonc`, runtime `AGENTS.md` (copied from
  `GLOBAL.md`), `GLOBAL.md`, `agents/`, `skills/`, and `standards/`.

Bash on Linux/macOS:

```bash
chmod +x ./install.sh
./install.sh
```

- Managed items are backed up before replacement by default, in a timestamped
  `.opencode-install-backup/<timestamp>/` directory inside the target.
- Use `--force` to replace managed items without backup.
- Installers manage `opencode.jsonc`, runtime `AGENTS.md` (copied from
  `GLOBAL.md`), `GLOBAL.md`, `agents/`, `skills/`, and `standards/`.

3. Restart opencode.

4. Optionally validate that the installed repo-managed surfaces still match this repo source:

```powershell
./doctor-opencode.ps1
```

- `doctor-opencode.ps1` requires PowerShell 7+.

```bash
./doctor-opencode.sh
```

- `doctor-opencode.sh` requires `python3`.
- These doctor scripts validate only the repo-managed files and directories
  installed by this repo. They are not general validators for arbitrary local
  customizations or extra active surfaces.

Default install target:

```text
~/.config/opencode
```

If `$XDG_CONFIG_HOME` is set, installers use:

```text
${XDG_CONFIG_HOME}/opencode
```

Custom target:

```powershell
./install.ps1 -Target "$HOME/.config/opencode"
```

```bash
./install.sh "$HOME/.config/opencode"
```

### Existing active surfaces

Installers do not delete untracked opencode surfaces. If an existing
`opencode.json`, `config.json`, `commands/`, `plugins/`, `modes/`, `agent/`, or
`skill/` is present in the target, the installer warns and leaves it untouched.
Those files/directories may still be loaded, merged, or otherwise affect
opencode behavior after install, so inspect them manually if behavior looks
stale or surprising.

### WSL caveat

Install and restart opencode in the same environment family (Windows vs WSL).
Configs under separate Windows and WSL config roots are not automatically shared,
so mixed installs can leave stale global config surfaces in both locations.

## Install Native Codex Setup

The Codex setup is a native adaptation of this ecosystem. It does not require
`--profile` for normal use.

```bash
chmod +x ./install-codex.sh ./doctor-codex.sh
./install-codex.sh
./doctor-codex.sh
```

Managed Codex items:

- `codex/AGENTS.md` -> `~/.codex/AGENTS.md`
- `codex/harness/` -> `~/.codex/harness/`
- `codex/agents/` -> `~/.codex/agents/`
- `codex/skills/*` -> `~/.agents/skills/`
- selected managed keys in `~/.codex/config.toml`

The installer backs up replaced managed files under
`~/.codex/.codex-ecosystem-backup/<timestamp>/` unless `--force` is used.

Codex workflow:

- Default conversational mode behaves like the opencode Mentor profile:
  consultative, standards-backed, friendlier for learning, and implementation
  only when explicitly asked.
- `/plan` behaves like Orc Plan: exploration, scope clarification, `.spec.md`
  creation/update inside the workspace, and precise handoffs.
- Implementation can still happen in the same main thread after scope is clear.
- Subagents are available for explicit delegation, review, reconciliation, and
  verification.
- Native Codex Memories stay disabled; persistent project memory flows through
  the local `agentMemory` MCP server.


## Agent Profiles

This setup includes primary profiles for day-to-day orchestration, planning,
implementation flow, and ask-mode mentoring. It also includes scoped subagents
for backend, frontend, database, DevOps, architecture review, security review,
reconciliation, documentation, memory retrieval, and verification tasks.

The Mentor profile stays read-only, but can now ask-gated web research when local
standards or model knowledge are insufficient. It is instructed to prioritize
official docs, specs, changelogs, and vendor documentation, and to treat Stack
Overflow or similar community sources as secondary signals rather than final
authority.

The built-in `explore` subagent is configured as a cheap read-only
`openai/gpt-5.4-mini` profile; `explore-mini` is also
`openai/gpt-5.4-mini` and used as fallback when the primary explorer is
unavailable.

Agent frontmatter keeps both the repo's `variant` intent and the OpenAI-effective
`reasoningEffort` option. `xhigh` and `high` variants map to
`reasoningEffort: high`; `medium` maps to `reasoningEffort: medium`. OpenAI's
standard reasoning-effort option has no `xhigh` value, so `xhigh` remains an
intent label while the runtime option is `high`.

It also includes a dedicated `documentation-writer`, a currently disabled native
`memory-retriever` placeholder for repo-backed memory-note verification,
`qa-builder` for scoped test work, a `tech-lead` for larger design-risk
reviews, and a restricted `worktree-manager` for safe parallel worktree
preparation.

The public README intentionally stays high level. Inspect the files under
`agents/` for exact model selections, permissions, and profile instructions before
installing or customizing them.

## Workflow

Use the default Orc Plan profile for normal orchestration and specs before
implementation. Switch to the Del Build profile when scope is clear, and to the
Mentor profile when you want ask-mode guidance without file edits.

`plan` does not implement changes, but it may create or update workspace spec
files ending in `.spec.md`. Use `.opencode/specs/` by default, or keep the
repo's stronger spec convention when one already exists, such as
`.codex/specs/`, `.claude/specs/`, or `docs/specs/`. It still cannot edit
non-spec files.

See `docs/neovide-opencode-workflow.md` for the recommended Neovide + OpenCode loop.

## V3 Native Runtime Contracts

The native OpenCode flow now uses V3 handoff and review contracts:

- `plan` can pass, and `build` expects, fields such as
  `size`, `mini`, `needs_qa`, `human_gate`, `reference_files`, `risk_flags`,
  `tech_lead_recommended`, `worktree_recommended`, and
  `max_rework_iterations`.
- `code-reviewer`, `architecture-reviewer`, and `security-reviewer` share the
  same exact top-level findings schema (`verdict`, `findings`,
  `open_questions`, `verification_gaps`) so `reconciler` can consume them
  directly.
- `reconciler` and `verifier` emit structured JSON findings/failures to support
  deterministic routing.
- `build` applies a single canonical gate: if `human_gate=true`, it pauses after
  `code-reviewer` and before reconciler; verifier/reconciler rework is capped at
  three attempts.
- `qa-builder` is only invoked when `needs_qa=true`, and its handoff must carry
  `spec`, `reference_files`, `allowed_test_paths`, and
  `verification_commands`.
- `tech-lead` is used when `size` is `L|XL` (or `tech_lead_recommended=true`).
- `agents`, `workflow runtime`, `installers/doctors`, and `public contracts`
  trigger required architecture/security review according to the same Mini-SDD
  risk guidance documented in `plan` and `build`.
- `worktree-manager` is limited to safe worktree operations (`git worktree
  list/add`, `git status --short`); `build` captures the returned paths,
  assigns at most one builder per writable path, and escalates cleanup instead
  of removing worktrees autonomously.

Evidence (native root): `agents/plan.md`, `agents/build.md`,
`agents/code-reviewer.md`, `agents/architecture-reviewer.md`,
`agents/security-reviewer.md`, `agents/reconciler.md`,
`agents/verifier.md`, `agents/qa-builder.md`, `agents/tech-lead.md`,
`agents/worktree-manager.md`.

## Standards

Load standards on demand via the `standards` reference. Start with:

```text
@standards/INDEX.md
```

Do not load every standard by default.

New mentoring-oriented standards cover software-design fundamentals, pattern
selection, repository organization, technology decisions, and technical web
research guardrails.

## MCP Memory

This setup declares the local persistent-memory MCP server `agent-memory`, but
keeps native persistent memory disabled by default and denied to agents pending
separate approval, so fresh installs do not fail when the local binary is
missing:

```jsonc
"mcp": {
  "agent-memory": {
    "type": "local",
    "command": ["{env:HOME}/.agent-memory/bin/agent-memory", "mcp"],
    "enabled": false
  }
}
```

Standard agents, including `memory-retriever`, are denied direct
`agent-memory` access (`permission.agent-memory_*` is `deny` in
`opencode.jsonc`). The native `memory-retriever` profile therefore only exists
to cross-check caller-provided memory notes against repo evidence; it must not
be used as an MCP escape hatch.

Additional MCPs for the native OpenCode root should stay optional and disabled
until a later spec defines platform details, credential flow, and least-
privilege permissions. Document candidates such as filesystem,
sequential-thinking, GitHub, Sentry, or deployment MCPs before adding live
config with commands or secrets.

The default command is POSIX-oriented and resolves to
`~/.agent-memory/bin/agent-memory mcp` when `$HOME` is set. Enable it only after
you have installed the binary or overridden the command for your environment.
Windows users should override the command or provide a compatible `HOME`
environment variable before enabling it. Keep tokens and machine-specific
secrets out of the repo.

## Worktree Safety

`worktree-manager` is intentionally narrow. It may only support:

- `git worktree list`
- `git worktree add`
- `git status --short`

It must not perform `git commit`, `git merge`, `git push`, `git reset`,
`git rebase`, `git clean`, or autonomous `git worktree remove` without explicit
human approval. Dirty or conflicted worktrees should block cleanup rather than
being force-resolved; `build` should escalate exact paths/status for human
cleanup.
