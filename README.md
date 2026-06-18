# opencode-ecosystem

Portable opencode setup for spec-first development, implementation assistance,
review, reconciliation, verification, and standards-backed mentoring.

## Includes

- `opencode.jsonc`: portable global config.
- `AGENTS.md`: short default global instruction set.
- `GLOBAL.md`: managed legacy compatibility file that points to `AGENTS.md`.
- `agents/`: primary and subagent profiles for planning, implementation, review,
  verification, and mentoring.
- `skills/`: reusable workflows for planning, review, reconciliation, and final
  checks.
- `standards/`: curated technical standards and opencode workflow guidance.
- `install.ps1`: copies this repo into `~/.config/opencode` (or `$XDG_CONFIG_HOME` if set) on Windows.
- `install.sh`: copies this repo into `~/.config/opencode` (or `$XDG_CONFIG_HOME`) on Linux/macOS.

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
- Installers manage `opencode.jsonc`, `AGENTS.md`, `GLOBAL.md`, `agents/`,
  `skills/`, and `standards/`.

Bash on Linux/macOS:

```bash
chmod +x ./install.sh
./install.sh
```

- Managed items are backed up before replacement by default, in a timestamped
  `.opencode-install-backup/<timestamp>/` directory inside the target.
- Use `--force` to replace managed items without backup.
- Installers manage `opencode.jsonc`, `AGENTS.md`, `GLOBAL.md`, `agents/`,
  `skills/`, and `standards/`.

3. Restart opencode.

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


## Agent Profiles

This setup includes primary profiles for day-to-day orchestration, planning,
implementation flow, and ask-mode mentoring. It also includes scoped subagents
for backend, frontend, database, DevOps, review, reconciliation, and verification
tasks.

The built-in `explore` subagent is overridden with a cheap read-only profile on
`opencode/deepseek-v4-flash-free`; `explore-mini` is available as an
`openai/gpt-5.4-mini-fast` fallback when DeepSeek is unavailable because GPT-5.4
Nano is not exposed by the current runtime. It can be switched to Nano when that
model becomes available.

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

This setup declares the local persistent-memory MCP server `agent-memory`.
It is disabled by default so fresh installs do not start with a failing MCP when
the external memory server is not installed yet:

```jsonc
"mcp": {
  "agent-memory": {
    "type": "local",
    "command": ["{env:HOME}/.agent-memory/bin/agent-memory", "mcp"],
    "enabled": false
  }
}
```

The default command is POSIX-oriented and resolves to
`~/.agent-memory/bin/agent-memory mcp` when `$HOME` is set. Enable it locally
after verifying the memory server install path, or override the MCP entry if your
binary lives elsewhere. Windows users should override the command or provide a
compatible `HOME` environment variable before enabling it. Keep tokens and
machine-specific secrets out of the repo.
