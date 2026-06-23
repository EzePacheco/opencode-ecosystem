# Neovide + OpenCode Workflow

This repo treats **Neovide** as the primary editor surface and **OpenCode** as
the orchestration, planning, implementation, review, and verification assistant.

## Recommended Loop

1. Open the project in Neovide.
2. Start OpenCode from the project root.
3. Use `plan` to clarify scope and, when useful, create/update a workspace
    `.spec.md` under `.opencode/specs/` by default or the repo's established
    spec locations such as `.codex/specs/`, `.claude/specs/`, or `docs/specs/`.
    `plan` still cannot edit non-spec files.
4. Switch to `build` only after the task or spec is decision-complete.
5. Switch to `build` with V3 handoff metadata (`size`, `mini`, `needs_qa`,
   `human_gate`, `reference_files`, `risk_flags`, `tech_lead_recommended`,
   `worktree_recommended`, `max_rework_iterations`).
6. Use subagents for focused work: builders, `code-reviewer`,
   `architecture-reviewer`, `security-reviewer`, `reconciler`, and `verifier`.
7. Reviewers share a common top-level JSON findings schema, and
   reconciler/verifier also return structured JSON; `build` can pause for
   `human_gate`, then on verifier failure run the unambiguous loop
   `verifier failure -> reconciler -> verifier` up to 3 rework iterations.
8. Return to Neovide for manual edits, local inspection, and normal coding flow.

## Why This Split Works

- Neovide stays fast for reading and editing.
- OpenCode keeps the task pipeline explicit: scope, spec, build, review,
   reconcile, verify, bounded rework.
- The standards reference stays available on demand via `@standards/INDEX.md`.

## Notes

- This repo does not manage Neovide or Neovim dotfiles.
- OpenCode runtime instructions for native installs come from `GLOBAL.md`.
- Codex files under `codex/` remain a reference harness, not the primary runtime.
- Evidence: `agents/plan.md`, `agents/build.md`, `agents/code-reviewer.md`,
  `agents/reconciler.md`, `agents/verifier.md`.
