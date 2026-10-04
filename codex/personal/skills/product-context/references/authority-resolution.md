# Authority resolution

Resolve Product identity and the scope in question before interpreting
sources. Use the Product's designated authorities; do not assume that a
particular tool or repository is the Product source of truth.

## Product authority

Authority depends on explicit designation, scope, provenance and status, not
on where content happens to appear. A ChatGPT Space is a Product knowledge
home only when the Product explicitly adopts it. Within that Space, only Pages
designated for the relevant scope can hold Product Authority. Membership in a
Space, Page presence, recency or a copied summary alone does not confer
authority.

Products without a Space continue to use their designated existing
authorities. Migration from a legacy source such as Notion can cover only some
scopes. Until an explicit cutover for a scope, its legacy authority remains in
force. Preserve conflicting current sources with their provenance and mark
the conflict VERIFY; do not silently choose or promote a proposal.

Use status and provenance appropriate to the evidence:

- **CONFIRMED** — an authorized Product decision is concrete and unambiguous;
  it may still need durable formalization.
- **PROPOSED** — under consideration, not current Product intent.
- **VERIFY** — authority, scope, status, decision or provenance is unclear, or
  current sources conflict.
- **SUPERSEDED / HISTORICAL** — retained for history, not current authority.
- **NEEDS_FORMALIZATION** — durable authority needs updating; this does not by
  itself invalidate a confirmed decision.

Classify a source for the scope being reconciled. Useful classes include
current authority, current reference, proposed/discovery, historical or
superseded, duplicate, and VERIFY. Content type or age alone does not settle
its class.

## Technical truth

Keep Product intent distinct from implementation and technical rationale:

- Confirmed Product authority answers what the Product should do.
- Current code, configuration, contracts, schemas, migrations, tests and
  relevant runtime evidence answer what is implemented.
- Accepted ADRs preserve technical rationale; active specs describe intended
  technical change while work is underway.
- Derived context, history, sessions and handoffs provide context but never
  silently override current authorities.

Inspect bounded technical questions directly. Use `repo-readiness` only when
repository preparation, documentation or harness readiness is the question.
Do not use it as the default mechanism for technical reads.

## Access and derived context

Capability and access are separate. ChatGPT may use authorized Space/Pages and
connected apps when the active surface exposes them. Do not imply that Codex
Local automatically receives ChatGPT Space, Project, Sources, Library or chat
content. For engineering work, rely on material Product decisions explicitly
transferred by the orchestrator or canonical references actually accessible
to Codex.

Do not reconstruct private ChatGPT context through browser/computer use,
connectors, caches or guessed local files unless the user explicitly requests
that specific resource retrieval and purpose. A missing input blocks only the
conclusions that depend on it.

A Project bridge, context note or migration plan is **DERIVED WORKING
CONTEXT**, never Product Authority. Prefer references to canonical sources
over copied content when the receiving surface can reliably use those
references.
