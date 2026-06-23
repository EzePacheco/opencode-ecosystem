---
name: spec
description: Use when the user asks OpenCode to create or update an executable spec, SDD artifact, acceptance-criteria document, or implementation-ready plan before code changes. When the active agent can edit workspace spec files, write a repo-local `*.spec.md`; otherwise return the exact spec content or handoff without editing product code.
---

# Spec

Create or update an executable spec before implementation.

Workflow:

1. Understand the user's desired outcome and current repo constraints.
2. Explore read-only before asking questions that local context can answer.
3. Read `@standards/INDEX.md`, then load only relevant standards.
4. Prefer the repo's existing spec convention when one exists. Otherwise default to `.opencode/specs/<slug>.spec.md`. Common valid locations include `.codex/specs/`, `.claude/specs/`, `docs/specs/`, or another workspace path ending in `.spec.md`.
5. Keep the spec concise and executable. Use the smallest template that fits the risk.

S/M spec shape:

```markdown
# SPEC: <title>

## Objective

## Context

## Requirements And Constraints

## Scope
Yes:
No:

## Acceptance Criteria
1.
2.

## Edge Cases

## Risks

## Implementation Slices

## Verification
```

L/XL additions:

- assumptions and open questions;
- inputs, outputs, and affected contracts;
- 2-4 alternatives when architecture, framework, database, ORM, DevOps,
  security, or structural refactor decisions are in play;
- decision criteria;
- ADR triggers;
- rollout, rollback, migration, and security/privacy implications;
- builder handoff with allowed files/layers, forbidden scope, contracts,
  expected checks, and review gates.

Rules:

- Do not edit product code while creating the spec.
- If the active agent cannot edit workspace `*.spec.md` files, return the exact spec content or file-ready handoff instead of attempting an edit.
- Do not load every standard.
- Make acceptance criteria verifiable by command, observable behavior, or concrete evidence.
- Call out unresolved product or architecture decisions instead of guessing.
- If a spec already exists for the same task, update it only when the new request changes scope or acceptance criteria.
- Do not force the L/XL template onto S/M work.
