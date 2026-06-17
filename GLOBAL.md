# Global Workflow

- Main thread default: orquestar, aclarar alcance, decidir routing y sintetizar.
- Antes de cargar standards, leer `@standards/INDEX.md` y abrir solo lo necesario.
- Para trabajo no trivial, producir spec antes de implementar.
- Builders implementan solo el slice asignado; no redisenan fuera de la spec.
- Toda entrega grande pasa por `code-reviewer`, luego `reconciler`, luego `verifier`.
- La memoria MCP es contexto util, pero debe validarse contra codigo, ADRs, changelogs o commits antes de usarla como fuente de verdad.
