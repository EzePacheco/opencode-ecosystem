# opencode-ecosystem

Portable global opencode setup for SDD, fan-out implementation, adversarial
review, reconciliation, and final verification.

## Includes

- `opencode.jsonc`: portable global config.
- `GLOBAL.md`: short default instruction set.
- `agents/`: orchestrator, planners, builders, reviewer, reconciler, verifier.
- `skills/`: SDD, adversarial review, reconcile, ship-check.
- `standards/`: curated technical standards and opencode workflow guidance.
- `install.ps1`: copies this repo into `~/.config/opencode` on Windows.

## Install On Another PC

1. Clone this repo.
2. Run PowerShell:

```powershell
./install.ps1
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

## Agent Map

### Main thread

- `orchestrator`
  - mode: `primary`
  - model: `openai/gpt-5.5`
  - role: default main-thread orchestrator
  - job: understand request, keep scope, route to Plan or Build, load standards on demand

- `plan`
  - mode: `primary`
  - model: `openai/gpt-5.5`
  - role: SDD/planning agent
  - job: create goal, scope, acceptance criteria, slices, and verification plan
  - permissions: read-only

- `build`
  - mode: `primary`
  - model: `openai/gpt-5.5`
  - role: delivery orchestrator
  - job: delegate builders, run review, send accepted findings to reconciler, then verify

### Builders

- `backend-builder`
  - mode: `subagent`
  - model: `openai/gpt-5-mini`
  - role: backend implementation only

- `frontend-builder`
  - mode: `subagent`
  - model: `openai/gpt-5-mini`
  - role: frontend implementation only

- `database-builder`
  - mode: `subagent`
  - model: `openai/gpt-5-mini`
  - role: schema, migrations, queries, persistence

- `devops-builder`
  - mode: `subagent`
  - model: `openai/gpt-5-mini`
  - role: CI, deploy, infra, observability, operability

### Review and closure

- `code-reviewer`
  - mode: `subagent`
  - model: `openai/gpt-5.5`
  - role: adversarial reviewer
  - job: find bugs, regressions, security issues, contract drift, test gaps, operability risks
  - permissions: read-only

- `reconciler`
  - mode: `subagent`
  - model: `openai/gpt-5.5`
  - role: applies accepted reviewer findings
  - job: minimal corrective changes and cross-builder integration cleanup

- `verifier`
  - mode: `subagent`
  - model: `openai/gpt-5-mini`
  - role: final verification agent
  - job: lint, build, tests, acceptance criteria coverage, residual risk reporting
  - permissions: read-only

## Workflow

```text
orchestrator
  -> plan
      -> spec / SDD
  -> build
      -> backend-builder
      -> frontend-builder
      -> database-builder
      -> devops-builder
      -> code-reviewer
      -> reconciler
      -> verifier
```

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
