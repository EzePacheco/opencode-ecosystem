---
name: workflow-sdd
description: Use when the user asks for a spec, SDD, planning, acceptance criteria, task slicing, scope clarification, or a decision-complete implementation handoff before implementation in Codex.
---

# Workflow SDD

Use this skill when the task is non-trivial and needs a spec before code.

Workflow:

1. Start from the user's actual problem and current constraints.
2. Read `~/.codex/harness/standards/INDEX.md`.
3. Load only the relevant standards.
4. Classify scope as S/M/L/XL with evidence from the repo or product context.
5. Produce goal, context, scope yes/no, affected contracts, edge cases, risks, acceptance criteria, implementable slices, and verification evidence.
6. For L/XL work, include alternatives considered, decision criteria, ADR triggers, rollout/rollback concerns, and security/privacy implications.
7. Make the handoff explicit enough that builders do not need to redesign.

Avoid:

- loading every standard;
- writing theory-heavy plans disconnected from the codebase;
- leaving scope or ownership ambiguous.
- validating the first proposed architecture without comparing viable options.

L/XL spec checklist:

- Requirements, constraints, assumptions, and open questions are separated.
- Boundaries and non-goals are explicit.
- Alternatives are compared against concrete criteria such as correctness,
  maintainability, security, operability, cost, reversibility, and team fit.
- Acceptance criteria are verifiable by command, observable behavior, contract
  evidence, or reviewer evidence.
- ADR triggers are called out when the decision affects architecture, contracts,
  dependencies, data, security, deploy, or workflow.
- Builder handoff states allowed files/layers, forbidden scope, contracts
  affected, checks expected, and the rule not to redesign outside the spec.
