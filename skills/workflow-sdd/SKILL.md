---
name: workflow-sdd
description: Use when the user asks for a spec, SDD, planning, acceptance criteria, task slicing, or scope clarification before implementation.
---

# Workflow SDD

Use this skill when the task is non-trivial and needs a spec before code.

Workflow:

1. Start from the user's actual problem and current constraints.
2. Read `@standards/INDEX.md`.
3. Load only the relevant standards.
4. Produce goal, context, scope yes/no, affected contracts, edge cases, risks, acceptance criteria, and implementable slices.
5. Make the handoff explicit enough that builders do not need to redesign.

Avoid:

- loading every standard;
- writing theory-heavy plans disconnected from the codebase;
- leaving scope or ownership ambiguous.
