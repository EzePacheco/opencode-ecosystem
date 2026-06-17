---
name: adversarial-review
description: Use when builder changes need a critical code review focused on bugs, regressions, security, contracts, and missing verification.
---

# Adversarial Review

Use this skill after implementation and before closing a substantial change.

Workflow:

1. Review the approved spec or explicit scope.
2. Inspect the combined diff and any verification evidence.
3. Prioritize correctness, security, contract stability, operability, and tests.
4. Report findings first, ordered by severity.
5. End with `accepted` or `rework-required`.

Do not focus on superficial style issues unless they imply a real risk.
