---
name: repo-readiness
description: Audit a Git repository or a selected repository set for Codex context, technical authorities, documentation, contracts, enforcement, feedback loops, and harness readiness. Use for explicit repository-readiness, documentation/harness review, or preparing a repo for Codex; do not use for ordinary implementation or code-review tasks.
---

# Repo readiness

Auditá proporcionalmente un repositorio Git y producí evidencia, findings y un plan. El comportamiento por defecto es estrictamente read-only: no crees, edites, instales, migres, despliegues ni ejecutes operaciones destructivas.

## Preflight

Antes del inventario o de cualquier check, resolvé el Git root/checkout y leé las instrucciones que aplican. Confirmá qué paths se pueden inspeccionar y cuáles deben quedar excluidos; verificá que el scanner pueda imponer esos límites antes de recorrerlos o leerlos. Inspeccioná el scanner/comando y sus efectos, y comprobá la disponibilidad de Python y Git antes del inventario. Para otros checks, inspeccioná scripts/configuración y disponibilidad de las dependencias locales antes de ejecutarlos. No instales dependencias ni reemplaces el runner canónico con shims o herramientas globales; si falta algo, informá el bloqueo y pedí la autorización o preparación faltante. Reutilizá discovery actual entre etapas si coinciden checkout, HEAD, estado local y alcance; ante cambios o duda, actualizá sólo los facts afectados.

## Workflow

Seguí siempre:

```text
DISCOVER → CLASSIFY → AUDIT → GAPS → PLAN → STOP
```

Modos:

- **Current repo:** si `cwd` o el path explícito está dentro de Git, resolvé ese Git root, decidí las exclusiones según la petición y ejecutá `scripts/repo_inventory.py` con las opciones necesarias antes de auditar ese repositorio.
- **Selected multi-repo:** fuera de Git, tratá el cwd como posible workspace y ejecutá una vez `scripts/workspace_inventory.py`; usá sus Git roots como candidatos, seleccioná sólo los pertinentes y ejecutá/reutilizá `repo_inventory.py` una vez por checkout seleccionado.

Para un inventario con límites de lectura, pasá `--respect-gitignore` para excluir antes del recorrido los paths ignorados no rastreados y `--exclude-path <ruta-relativa>` una o más veces para excluir un archivo o subárbol relativo al Git root, incluso si está rastreado. Un ejemplo para omitir workflows es `--exclude-path .github/workflows`. Estas rutas son literales, no patrones. Sin esas opciones el recorrido conserva el comportamiento existente. Git ignore por sí solo nunca excluye un archivo ya rastreado; los rastreados quedan incluidos salvo exclusión explícita. Si Git no puede determinar de forma acotada los paths ignorados, el scanner falla cerrado y el inventario queda bloqueado, no parcial respecto de esa protección.

Leé [references/multi-repo.md](references/multi-repo.md) sólo para sweeps. Leé [references/profiles.md](references/profiles.md) cuando el perfil no sea obvio o haya varios repos, componentes o riesgo. Leé [references/audit-rubric.md](references/audit-rubric.md) para una auditoría interpretativa.

## Frontera scanner / Codex

El scanner produce únicamente facts mecánicos, deterministas, bounded y JSON-friendly. Codex interpreta esos facts según riesgo, ownership, lifecycle y comportamiento observable. El scanner no debe decir que un repo está mal, que necesita tests o que una instrucción es demasiado grande.

El schema JSON actual sigue siendo `2`. Incluye estado local de Git, hasta 50 commits locales (`commits_inspected`, `limit_reached`) y sus identidades de autor, más paths/tamaños de contributor guides, CODEOWNERS y templates de PR/MR encontrados. Con exclusiones opt-in, `warnings` indica si se aplicó Git ignore y cuántas reglas explícitas se usaron; el resto del schema no cambia. Estos datos son evidencia acotada, no una decisión de que el repo sea compartido. La cobertura permanece sujeta a los límites de recorrido e historial reportados.

El workspace padre es scope de coordinación, no Technical Authority. Cada Git repository conserva sus propias instrucciones, contracts, checks y estado. En workspaces no-Git consultá [references/multi-repo.md](references/multi-repo.md); los scanners reportan facts y Codex interpreta pertenencia, relevancia y selección.

No ejecutes automáticamente scripts del repositorio por llamarse `lint`, `test` o `check`. Sólo ejecutá validaciones claramente read-only, locales, bounded, baratas, sin `--fix`, migraciones, red, secretos ni efectos persistentes.

## Integración opt-in con MemoriesAI

`repo-readiness` permanece read-only por defecto. Cuando el usuario autoriza
persistencia histórica, el flujo es:

```text
CURRENT FACTS → CURRENT INTERPRETATION → optional previous readiness snapshot → DELTA → optional persistence
```

La skill puede consultar snapshots especializados con:

```bash
memoryctl readiness-audit latest --repo-path <repo> --json
memoryctl readiness-audit history --repo-path <repo> --limit N --json
```

Sólo con instrucción explícita puede persistir el resultado sintetizado:

```bash
memoryctl readiness-audit put --repo-path <repo> --stdin-json
```

Se conserva un snapshot compacto, nunca raw scanner JSON ni el informe completo.
MemoriesAI resuelve `repository_id`, registry, Git root y normalización de
identidad; no se duplican esas lógicas aquí. La identidad estable de un finding
es `area | authority_key | subject_key`, sin incluir `action`.

La auditoría corriente siempre se construye desde los hechos actuales. La
memoria previa sólo se usa después para calcular delta y nunca pre-seedea los
findings actuales.

## Clasificación resumida

- **D1:** propósito único, pocos boundaries, bajo riesgo y feedback directo.
- **D2:** módulos o runtimes relevantes, persistence, schemas, contracts o decisiones materiales.
- **D3:** alto blast radius, seguridad/tenancy/dinero/PII, migraciones, compatibilidad, operación continua o coordinación multi-repo.

No clasifiques sólo por LOC o cantidad de archivos. Considerá también library, documentation/planning, monorepo y multi-repo product.

## Findings

Usá sólo cuando haya evidencia y acción proporcional:

`KEEP` · `SIMPLIFY` · `ENFORCE` · `ADD` · `REMOVE` · `DEFER` · `VERIFY`

Formato compacto:

```text
[PRIORITY] ACTION — Área
Evidence:
Risk/cost:
Affected authority:
Mechanically enforceable: yes|no|partial
Recommendation:
Confidence: high|medium|low
```

## Output obligatorio

Incluí siempre:

```text
REPO PROFILE
CONTEXT LOAD
AUTHORITIES
GAPS
DO NOT ADD
NEXT ACTIONS
```

Incluí sólo si hay evidencia relevante: `DOCUMENTATION`, `CONTRACTS`, `ARCHITECTURE`, `ENFORCEMENT`, `FEEDBACK LOOPS`, `TEAM PORTABILITY`, `SHARED CONTRIBUTOR CONTRACT`, `HARNESS`. Cuando haya evidencia de colaboración o el usuario declare un repo compartido, evaluá las dos dimensiones de equipo según la rúbrica. En `HARNESS`, distinguí decisiones sobre AGENTS local, contributor contract, skills locales, enforcement mecánico y documentación durable adicional; referenciá findings sin repetirlos. No rellenes secciones vacías con generalidades. No uses un score numérico agregado.

Toda auditoría debe terminar con `DO NOT ADD` y detenerse después del plan.

## Regla central

> Toda nueva capa debe resolver un problema actual respaldado por evidencia.

`absence != need` · `personal configuration != repository/team contract` · `existing != still needed`.

La configuración personal no sustituye reglas repo-specific compartidas. Evaluá su portabilidad sin convertir colaboración en complejidad ni exigir archivos por convención; reevaluá también el propósito de los existentes.

La ausencia de una herramienta no constituye necesidad. No recomiendes automáticamente TypeScript, frameworks de tests, Playwright, ADRs, `LLM_CONTEXT`, observabilidad, skills, hooks, formatters, routers documentales, arquitectura ceremonial o CI adicional.

No implementes findings durante una auditoría.
