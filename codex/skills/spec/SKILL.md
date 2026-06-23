---
name: spec
description: Use when the user asks Codex to create or update an executable spec, SDD artifact, acceptance-criteria document, or implementation-ready plan before code changes. The skill writes a scoped spec under `.codex/specs/` without editing product code.
---

# Spec

Create or update an executable spec before implementation.

Workflow:

1. Understand the user's desired outcome and current repo constraints.
2. Explore read-only before asking questions that local context can answer.
3. Read `~/.codex/harness/standards/INDEX.md`, then load only relevant standards.
4. Create `.codex/specs/<slug>.spec.md` unless the repo already has a stronger spec convention.
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
- Do not load every standard.
- Make acceptance criteria verifiable by command, observable behavior, or concrete evidence.
- Call out unresolved product or architecture decisions instead of guessing.
- If a spec already exists for the same task, update it only when the new request changes scope or acceptance criteria.
- Do not force the L/XL template onto S/M work.
