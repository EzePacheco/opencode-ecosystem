---
name: ship-check
description: Use when a Codex task is functionally done and needs final lint, build, test, and acceptance-criteria verification before handoff.
---

# Ship Check

Use this skill at the end of a coding task.

Workflow:

1. Run the relevant lint, build, test, and typecheck commands.
2. Compare the result against the approved spec or scope.
3. Call out skipped or blocked checks explicitly.
4. Summarize residual risk.
5. Return a clear verdict: `accepted`, `partially-verified`, or `rework-required`.
