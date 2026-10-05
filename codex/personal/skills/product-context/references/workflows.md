# Workflows

Select only the workflow needed. Keep outputs compact and distinguish evidence,
recommendations and unresolved VERIFY. Do not create artifacts unless the
workflow and user authorization call for them.

## AUDIT / REFRESH

Read-only. Resolve Product and scope, identify designated authorities and
pertinent repositories, then assess coverage, currency, provenance, conflicts,
gaps and material drift. Inspect bounded technical evidence directly.

When useful, compare Product current/target state with technical current state:

- **ALIGNED** — intent and relevant behavior coincide.
- **PRODUCT_AHEAD** — Product target exists; implementation is pending.
- **IMPLEMENTATION_AHEAD** — implementation is newer and a concrete,
  authorized Product decision is confirmed but not durably formalized.
- **CONFLICT / VERIFY** — the difference or its provenance cannot be resolved.

Keep Product authority as evidence of intent and current repository/runtime
evidence as technical truth. Report recommended actions and what should not be
added. Do not mutate sources, create a context pack, or persist the audit.

## INGEST / RECONCILE

Start read-only. Classify supplied material by authority, status, scope and
provenance; identify what it confirms, changes, supersedes, duplicates or
conflicts with; assess Product and technical impact; and propose canonical
destination, history handling and reconciliation steps. A new document or
Page is not automatically authoritative. Apply changes only when authorized.

For a Notion-to-Space migration, reconcile meaning and authority rather than
copying pages byte-for-byte. Consider durable Product context, accepted
decisions, requirements and flows, authoritative roadmap/scope, terminology
and durable open questions. Do not automatically migrate stale or duplicate
summaries, raw meeting history, personal scratchpads, obsolete discovery,
repository facts cheaper to inspect in code, or operational databases whose
semantics Pages cannot safely preserve.

Map each in-scope source to its proposed class and destination as needed:
current authority, current reference, proposed/discovery,
historical/superseded, duplicate or VERIFY. Preserve provenance and identify
conflicts and unmigrated scopes. A source manifest is useful only when a
multi-source migration needs it to track mapping or provenance.

If the active ChatGPT surface can write Space and the user authorized applying
the migration, create or update candidate Pages as appropriate. Otherwise
return the reconciliation plan/content and state that application remains
pending. Creating or updating a Page does not itself perform Product-authority
cutover; cutover must be explicit for the relevant scope. Keep legacy sources
authoritative for scopes not yet cut over.

## PROJECT BRIDGE

Optional. First decide whether a real Project access/context gap exists. If
current ChatGPT context already exposes the needed Product authority, do not
create a bridge. Prefer canonical Page references when the Project surface can
reliably use them.

When useful, provide only the minimum derived working context, such as:

- Product identity and canonical Product home;
- authority references and scope;
- material active Product decisions needed in Project context;
- unresolved Product VERIFY;
- a relevant repository map or migration/cutover status.

A bridge is Product context, not an exhaustive technical execution plan. A
brief guide can state the relevant goal, limits, acceptance and provenance;
Codex inspects the repository and chooses its plan. Add only material risks,
contracts and decisions, without a mandatory pack, manifest or control header.

Label a bridge **DERIVED WORKING CONTEXT**. It is not authority and should not
duplicate the Product source of truth. There is no universal output directory
or mandatory filename. Do not create or upload it unless authorized. When a
material Product decision must reach Codex, instruct the orchestrator to
transfer that decision explicitly; do not expect Codex Local to load the
Project bridge or other private ChatGPT context.
