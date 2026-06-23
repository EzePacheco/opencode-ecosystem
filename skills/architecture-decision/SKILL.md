---
name: architecture-decision
description: Guide architecture decisions, system design choices, technology selection, ADR drafting, and structural refactor planning. Use when OpenCode must compare architecture options, evaluate trade-offs, decide whether an ADR is needed, review durable technical choices, or prepare an implementation handoff for a significant design change.
---

# Architecture Decision

Use this skill when a task changes architecture, contracts, dependencies, data
ownership, deployment, security boundaries, or the team's development workflow.

## Workflow

1. Read the repo-local `AGENTS.md` and relevant docs, specs, ADRs, code, and tests.
2. Read `@standards/INDEX.md`, then load only relevant standards.
3. Separate requirements, constraints, preferences, assumptions, and open questions.
4. State the decision scope and what is explicitly out of scope.
5. Compare 2-4 viable options when more than one responsible path exists.
6. Evaluate options against concrete criteria: correctness, maintainability,
   security, operability, performance, cost, reversibility, migration effort,
   team fit, and customer/project requirements.
7. Recommend one path only after the trade-offs are clear.
8. Identify ADR triggers, rollout/rollback needs, tests, and review gates.
9. Produce a builder-ready handoff when implementation is requested.

## ADR Trigger

Create or request an ADR when the decision affects:

- architecture, module boundaries, data ownership, or public contracts;
- framework, language, provider, ORM, database, queue, cache, or deployment;
- security, auth, tenant isolation, privacy, payments, webhooks, or secrets;
- migration strategy, rollout, rollback, or operational behavior;
- an exception to a mandatory standard.

## Output Shape

Use the smallest structure that fits the decision:

- Direct recommendation for small, reversible choices.
- Options matrix for meaningful trade-offs.
- ADR-ready summary for durable choices.
- Builder handoff for approved implementation.

For ADR-ready output, include:

- context;
- decision;
- alternatives considered;
- consequences;
- risks;
- rollback or reversal path;
- links to code, specs, standards, or docs used as evidence.

## Guardrails

- Do not validate the first proposed architecture by default.
- Do not invent standards or cite irrelevant ones.
- Do not add ceremony for small reversible changes.
- Do not let builders redesign architecture after a decision-complete spec exists.
- Do not treat memory, generated docs, or old plans as truth without repo evidence.
