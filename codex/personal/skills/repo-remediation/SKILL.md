---
name: repo-remediation
description: Remediate current, explicitly requested repo-readiness or harness findings using isolated local Git worktrees by default, verify and re-audit affected boundaries, and complete explicitly authorized local integration. Do not use for ordinary feature work or fixes unrelated to readiness findings.
---

# Repo remediation

Convert current `repo-readiness` findings into only those changes that are actionable and authorized. This skill defaults to isolated local worktrees and integrates verified changes into an explicitly authorized local destination when requested. It does not duplicate the readiness scanner or rubric and does not make commits, push, open PRs, deploy, publish, run production migrations, or clean up worktrees.

## Preflight

Before discovery, inventory or verification, resolve the selected checkout and its applicable instructions; confirm read/write scope, excluded paths, and command effects. Inspect the inventory/check scripts and configuration; verify Python and Git for local scanners, and resolve each project runner/dependency from that checkout and its lockfile before executing it. Do not install automatically, run an uninspected lifecycle or project command, or substitute a shim/global runner for the canonical one. If a required dependency or authorization is missing, stop only the dependent check and ask for the missing preparation or approval. Carry the same exclusions into baseline and post-change evidence.

## Workflow

```text
DISCOVER → BASELINE AUDIT → CLASSIFY → PLAN → HUMAN GATE WHEN REQUIRED
→ ISOLATE → IMPLEMENT → FOCAL VERIFY → AFFECTED-BOUNDARY VERIFY
→ RE-AUDIT → REPAIR LOOP IF NEEDED → AUTHORIZED LOCAL INTEGRATION IF REQUESTED
→ FINAL STATE → STOP
```

1. Resolve the scope using `repo-readiness` discovery. If the CWD is not in Git, run its `scripts/workspace_inventory.py` once and select only relevant Git repositories. Reuse its current discovery facts; do not write another scanner or repeat an unchanged inventory.
2. Establish current baseline evidence for the selected finding before changing anything. A supplied report can be reused only after confirming it refers to the same checkout/root and `git_common_dir`, branch, HEAD, local diff/dirty state, and inventory scope/exclusions. Record these facts with finding identity, action, evidence, and affected repo/boundary. If a fact is absent, changed, or uncertain, refresh the affected discovery/inventory; do not treat an earlier report as current by assumption.
3. Classify each current finding as `KEEP`, candidate `ADD`/`SIMPLIFY`/`ENFORCE`/`REMOVE`, `VERIFY`, or `DEFER`; also identify `EXTERNAL` actions and unresolved authority as `STOP`. Then assign an outcome: `ACTIONABLE + AUTHORIZED`, `ACTIONABLE BUT NEEDS APPROVAL`, `VERIFY`, `DEFERRED`, `EXTERNAL`, or `STOPPED`. A finding alone does not authorize a change.
4. Plan each authorized change with its finding/evidence, desired state, owning repo/boundary, proposed change, dependencies/order, acceptance, and proportional verification. Group findings when one coherent change resolves them.
5. Stop only the affected change when Product behavior or material authority is unresolved, an irreversible/external action is required, or approval before planning was requested. Prepare the plan without mutating. Do not turn `VERIFY`, `DEFER`, or `STOP` into fixes.
6. Isolate every affected repository in its own local worktree and dedicated branch when safely possible. Use the existing base checkout only for an explicitly authorized local integration after verification, or an explicitly authorized direct-edit scope with a preservation baseline; do not infer this authorization from a finding. Preserve dirty work; never stash, reset, overwrite, or move it automatically. Record the isolation facts before making changes.
7. Implement the minimum coherent change, following each repository's applicable instructions and authorities. For every change, run the cheapest meaningful focal check, then checks for affected boundaries and consumers; expand checks for higher-risk contracts or data boundaries. Use the canonical runner from that checkout. If it is unavailable, report the blocker instead of silently substituting a shim; installation or other environment preparation needs its own authorization.
8. Re-audit the changed boundary using current evidence from the resulting worktree. Run the full `repo-readiness` inventory when permitted and proportionate. If authorized exclusions or scope prevent a complete inventory, perform a focal re-audit of only the selected finding: verify current checkout/root, HEAD and local diff state, inspect the changed rule/paths and its focal check results, then classify that finding. Mark every out-of-scope finding `NOT EVALUATED`; do not call it resolved, and do not imply whole-repository convergence. For a full re-audit, compare each finding as `RESOLVED`, `REMAINS`, `CHANGED`, `NEW`, `VERIFY`, `DEFERRED`, `EXTERNAL`, or `STOPPED`. A baseline is not post-change evidence. Refresh any evidence whose files, contracts, scope, HEAD or diff state changed; keep unchanged authorities only when their currentness is established.
9. Repair and verify new gaps caused by the changes and remaining actionable, authorized findings, then re-audit. Stop when those findings are resolved, authority is needed, progress stalls, or another change is no longer justified. Do not loop indefinitely.
10. When the user requests an operational local result, integrate the verified change into the explicitly authorized checkout or installed target. Before transferring, revalidate destination identity, revision and the exact affected staged/unstaged/untracked content against the preservation baseline. Attribute overlaps instead of overwriting them; stop only a material unresolved conflict. Back up the exact affected targets privately, including absence, then apply only the reviewed paths/delta. Read back the resulting content and run affected checks at the destination; worktree checks alone do not prove the installed result. Roll back only this change and only where content still matches the failed delivery; preserve later edits. If integration is not authorized or safe, deliver the inspectable result and state the specific pending action. Publication, services and changes to security permissions require their own concrete authorization.
11. Report the final state, checks and results, unresolved categories, and worktree locations/status. Distinguish prepared, locally integrated and published. Do not close with isolated patches alone when safe local integration was explicitly requested. Leave worktrees for inspection; never remove branches or worktrees automatically.

Read [isolation and convergence](references/isolation-and-convergence.md) for dirty checkout handling, multi-repo/worktree identity, state tracking, and stop conditions. Use Git CLI directly; add a helper only if repeated deterministic lifecycle work is demonstrated.

## Done

Done for the authorized scope means there are no remaining actionable and authorized `ADD`/`SIMPLIFY`/`ENFORCE`/`REMOVE` findings in that scope; required focal and affected-boundary checks pass on the delivered state; explicitly requested local integration has readback and destination verification; cross-repo acceptance is demonstrated where relevant; re-audit introduces no material gap; and remaining `VERIFY`/`DEFER`/`EXTERNAL`/`STOP`/`NOT EVALUATED` items are explicit. A focal re-audit can close its finding, but cannot establish whole-repository readiness. It does not require an empty gaps list or removal of every warning or suggestion.

Never claim an external/manual action was resolved by local changes. Never commit, push, deploy, publish, run production migrations, or automatically clean up worktrees.
