# Isolation and convergence

## Resolve repositories

- If CWD is within Git, use `repo-readiness` current-repository discovery and identify that checkout's Git root.
- Otherwise treat CWD as a possible non-Git workspace and reuse `repo-readiness/scripts/workspace_inventory.py`. Its roots are candidates; select only repos in the remediation scope.
- A repository is identified by its Git common directory. Multiple checkout paths with the same common directory are worktrees of one repository, not independent repositories. Separate common directories are separate repos. In a multi-repo run, isolate and report each affected repo independently; a shared run ID may connect their records.
- Read applicable `AGENTS.md` instructions from each affected repository before editing. The workspace parent coordinates; it does not define child repository behavior.

## Before isolation

For each affected checkout record its path, Git common directory, current branch or detached HEAD, base ref and SHA, porcelain dirty status (including untracked files), and existing worktree paths. This is the preservation baseline. Do not infer that dirty state is unrelated; inspect only enough to determine whether an isolation operation could overwrite or depend on it.

Prefer creating a separate worktree and a dedicated local branch from the recorded base SHA. Check whether the branch name or target worktree path already exists first. Never repurpose, move, delete, or overwrite an existing branch/worktree. If the base checkout has relevant dirty work, leave it intact and choose a safe base/transfer approach only when ownership and content are clear; otherwise stop that repo and report the blocker. Never use stash/reset as an isolation shortcut. Do not fetch or push as part of isolation.

If worktree creation is unavailable or unsafe, do not silently fall back to editing the base checkout. Report the concrete constraint and use another isolated checkout only when its identity and base are clear; otherwise stop before mutation.

## Evidence freshness and focal re-audit

Reuse discovery/inventory facts between `repo-readiness`, `architecture-health` and remediation only when they describe the same checkout path, Git common directory, branch, HEAD, local diff/dirty state and scope/exclusion options. Carry this compact snapshot in the existing conversation or report; do not create another coordination store. For a dirty checkout, compare staged, unstaged and untracked state and the affected paths. If the exact relevant state cannot be established, refresh the affected evidence before relying on it.

Any code, rule, test, contract, checkout revision or scope change invalidates earlier evidence for that affected boundary. A post-change baseline must be produced from the resulting worktree; do not reuse pre-change scanner facts to claim a fix. Unchanged authorities may be reused only after confirming they were not changed and remain in scope.

The normal post-change path is a full `repo-readiness` re-audit when permitted. When an explicit user exclusion or bounded authorization makes that inventory impermissible, re-audit only the selected finding: confirm current checkout identity, HEAD and local diff state; inspect the current changed paths; and record focal verification evidence. Mark other findings `NOT EVALUATED`, separately from `RESOLVED`, `REMAINS`, `CHANGED` or `NEW`. A focal result closes only the selected finding and is not repository-wide convergence.

Create worktrees only for repos that will change. In cross-repo work, identify contract owners and affected consumers, sequence compatible changes, and verify at the consumer boundary. Do not imply atomic cross-repo commits.

## Run state and comparison

For a long or multi-repo run, keep one compact state artifact in a temporary/local location outside product repos. Include only a run ID, repo/base SHA/worktree mapping, baseline findings, resolved and pending items, verify/deferred/external/stopped items, checks/results, and next step. It is a progress record, not Product or Technical Authority. For short single-repo work, the conversation and final summary are enough.

Compare post-remediation findings against the baseline using `repo-readiness`'s finding identity and evidence, not text similarity alone:

- `RESOLVED`: the evidenced gap is absent or its acceptance condition is now met.
- `REMAINS`: same material gap persists.
- `CHANGED`: same underlying subject has materially different evidence or action.
- `NEW`: post-audit gap not in baseline, including one introduced by the changes.
- `VERIFY`, `DEFERRED`, `EXTERNAL`, `STOPPED`: retain their status and state what evidence, authority, manual action, or decision is missing.

Reassess changed/new findings through the existing readiness rubric. Do not widen the scanner or treat a changed recommendation as permission. Continue only for newly introduced gaps or remaining actionable, authorized findings. Stop on missing authority, unsafe isolation, unavailable external action, repeated failure without progress, or when the next proposed change is not clearly justified. State why and leave the worktree inspectable.

## Verification and closeout

For each coherent change, record acceptance and run a focal check followed by the affected-boundary check. Expand proportionally for public contracts, persistence, authorization/tenancy, money, concurrency, external integrations, and cross-repo consumers. Do not run a full suite after every edit. If a broad check exposes a localized failure, reproduce and fix narrowly, rerun that failing check and the affected boundary, finish independent checks, then run broad confirmation once at the appropriate gate.

Close with changed repos and worktree paths, final branch/base SHA and dirty status, implemented findings and acceptance evidence, verification results, re-audit comparison, unresolved statuses, and the reason for any stop. Leave worktrees in place. Cleanup is a separate explicit request; if ever performed, first verify that only run-owned worktrees are targeted and refuse to remove any with unpreserved changes. Never delete branches automatically.
